import os
import sys
import math
import importlib
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTableWidgetItem, QLineEdit,
    QPushButton, QLabel, QHBoxLayout, QMessageBox, QHeaderView, QButtonGroup
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize, QEvent, QTimer, QItemSelection, QItemSelectionModel

# Load module UI cùng thư mục (xử lý tiền tố số 01_ theo convention)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
ICON_DIR = os.path.join(ROOT_DIR, "Images", "icons")

ui_module = importlib.import_module("01_MainScreen")
Ui_MainScreen = ui_module.Ui_MainScreen


class MainScreen_Ext(QMainWindow, Ui_MainScreen):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Biến trạng thái: "HE_10" hoặc "HE_4"
        self.che_do_diem = "HE_10"
        # Dòng làm mốc khi chọn nhiều dòng bằng Shift
        self.dong_neo = None
        # Chặn hiện nhiều hộp thoại lỗi chồng nhau
        self._dang_bao_loi = False

        self._cai_dat_icon_svg()
        self._cai_dat_cong_thuc()
        self._cai_dat_nhom_nut_he()
        self._cai_dat_bang()
        self._ket_noi_su_kien()
        self._khoi_tao_du_lieu_mau()
        self._cap_nhat_goi_y_theo_he()
        self.tinh_gpa_hien_tai()

    def _cai_dat_icon_svg(self):
        """Nạp icon SVG đồng bộ từ Images/icons"""

        def set_label(label: QLabel, name: str):
            path = os.path.join(ICON_DIR, name)
            if os.path.exists(path):
                label.setPixmap(QPixmap(path))
                label.setScaledContents(True)  # QSS padding sẽ tự co icon

        set_label(self.lbl_header_icon, "graduation-cap_white.svg")
        set_label(self.icon_credits, "book-open_blue.svg")
        set_label(self.icon_points, "star_blue.svg")
        set_label(self.icon_scale, "award_blue.svg")
        set_label(self.icon_target, "target_white.svg")
        set_label(self.icon_info, "lightbulb_white.svg")

        self._gan_noi_dung_nut(self.btn_them_mon, "plus_white.svg", "Thêm môn học", "#FFFFFF")
        self._gan_noi_dung_nut(self.btn_xoa_mon, "trash-2_dark.svg", "Xóa dòng chọn", "#16181E")
        self.btn_xoa_mon.setToolTip(
            "Giữ Shift để chọn nhiều dòng liên tiếp, giữ Ctrl (⌘ trên Mac) để chọn từng dòng rời")

    def _gan_noi_dung_nut(self, btn: QPushButton, ten_icon: str, noi_dung: str, mau_chu: str):
        KHOANG_CACH_ICON_CHU = 12
        btn.setText("")

        lay = QHBoxLayout(btn)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(KHOANG_CACH_ICON_CHU)
        lay.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        lbl_icon = QLabel()
        lbl_icon.setFixedSize(18, 18)
        path = os.path.join(ICON_DIR, ten_icon)
        if os.path.exists(path):
            lbl_icon.setPixmap(QIcon(path).pixmap(QSize(18, 18)))
        lbl_icon.setStyleSheet("background: transparent; border: none; padding: 0;")

        lbl_chu = QLabel(noi_dung)
        lbl_chu.setStyleSheet(
            f"background: transparent; border: none; padding: 0; "
            f"color: {mau_chu}; font-weight: 700; font-size: 13px;")

        # Để click xuyên qua label xuống nút
        for w in (lbl_icon, lbl_chu):
            w.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            lay.addWidget(w)

    def _cai_dat_nhom_nut_he(self):
        self.group_he_diem = QButtonGroup(self)
        self.group_he_diem.setExclusive(True)
        self.group_he_diem.addButton(self.btn_he_10)
        self.group_he_diem.addButton(self.btn_he_4)

        self.btn_he_10.setChecked(True)
        self.btn_he_10.clicked.connect(lambda: self._chuyen_che_do_he("HE_10"))
        self.btn_he_4.clicked.connect(lambda: self._chuyen_che_do_he("HE_4"))

    def _chuyen_che_do_he(self, che_do: str):
        """Xử lý khi người dùng chuyển giữa Hệ 10 và Hệ 4"""
        if self.che_do_diem == che_do:
            return

        che_do_cu = self.che_do_diem
        self.che_do_diem = che_do

        # Cập nhật tiêu đề cột điểm và thẻ quy chế
        if che_do == "HE_10":
            self.lbl_scale_title.setText("Thang Điểm Quy Đổi (Theo Thang 10)")
            self._cap_nhat_card_scale_he_10()
        else:
            self.lbl_scale_title.setText("Thang Điểm Quy Đổi (Theo Thang 4)")
            self._cap_nhat_card_scale_he_4()

        # Tự động quy đổi giá trị trong các ô điểm hiện có
        for r in range(self.tbl_mon_hoc.rowCount()):
            txt_score = self.tbl_mon_hoc.cellWidget(r, 2)
            if txt_score and txt_score.text().strip():
                hop_le_cu, _ = self.kiem_tra_diem(txt_score.text(), che_do_cu)
                try:
                    if not hop_le_cu:
                        # Điểm đang sai ở thang cũ thì giữ nguyên, để kiểm tra lại theo thang mới
                        raise ValueError
                    val = float(txt_score.text().strip().replace(",", "."))
                    if che_do_cu == "HE_10" and che_do == "HE_4":
                        # Đổi từ 10 sang 4 xấp xỉ
                        val_4 = min(4.0, max(0.0, (val / 10.0) * 4.0))
                        txt_score.setText(f"{val_4:.2f}")
                    elif che_do_cu == "HE_4" and che_do == "HE_10":
                        # Đổi từ 4 sang 10 xấp xỉ
                        val_10 = min(10.0, max(0.0, (val / 4.0) * 10.0))
                        txt_score.setText(f"{val_10:.1f}")
                except ValueError:
                    pass
            self._on_score_text_changed(r)

        # Quy đổi luôn ô GPA mục tiêu nếu đang hợp lệ ở thang cũ
        text_mt = self.txt_gpa_muc_tieu.text().strip().replace(",", ".")
        try:
            mt = float(text_mt)
            if 0 <= mt <= self.DIEM_TOI_DA[che_do_cu]:
                if che_do_cu == "HE_10":
                    self.txt_gpa_muc_tieu.setText(f"{mt / 10.0 * 4.0:.2f}")
                else:
                    self.txt_gpa_muc_tieu.setText(f"{mt / 4.0 * 10.0:.1f}")
        except ValueError:
            pass

        # Cập nhật lại tiêu đề cột, gợi ý nhập, GPA, tổng điểm và công thức theo hệ vừa chọn
        self._cap_nhat_goi_y_theo_he()
        self._cai_dat_cong_thuc()
        self.tinh_gpa_hien_tai()

    def _cai_dat_bang(self):
        """Cấu hình bảng tbl_mon_hoc 5 cột chuẩn"""
        header = self.tbl_mon_hoc.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Tên môn học
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # Số tín chỉ
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Điểm số
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Điểm chữ
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # Thao tác

        self.tbl_mon_hoc.setColumnWidth(1, 130)  # Số tín chỉ
        self.tbl_mon_hoc.setColumnWidth(2, 190)  # Điểm số
        self.tbl_mon_hoc.setColumnWidth(3, 130)  # Điểm chữ
        self.tbl_mon_hoc.setColumnWidth(4, 90)  # Thao tác

        self.tbl_mon_hoc.verticalHeader().setVisible(False)
        self.tbl_mon_hoc.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        # Cho phép chọn nhiều dòng (Shift: chọn một dãy, Ctrl/⌘: chọn từng dòng)
        self.tbl_mon_hoc.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tbl_mon_hoc.setShowGrid(False)
        self.tbl_mon_hoc.selectionModel().selectionChanged.connect(self._cap_nhat_giao_dien_chon)

    def eventFilter(self, obj, event):
        """
        Các ô nhập nằm đè lên dòng nên không tự chọn dòng được.
        Bắt click trên các ô này để chọn dòng, hành vi giống Excel:
        - Click thường: chọn riêng dòng đó, đặt làm dòng mốc
        - Shift + click: chọn dãy từ dòng mốc đến dòng vừa click (dòng mốc giữ nguyên)
        - Ctrl/⌘ + click: thêm hoặc bỏ một dòng, dòng đó thành dòng mốc mới
        - Ctrl/⌘ + Shift + click: thêm dãy từ dòng mốc vào vùng đang chọn
        Trên macOS, Qt đổi vai trò: phím ⌘ là ControlModifier, phím Control là MetaModifier,
        nên chấp nhận cả hai.
        """
        if event.type() == QEvent.Type.MouseButtonPress and obj.property("o_trong_bang"):
            row = self.tbl_mon_hoc.indexAt(obj.pos()).row()
            if row >= 0:
                phim = event.modifiers()
                KM = QtCore.Qt.KeyboardModifier
                co_shift = bool(phim & KM.ShiftModifier)
                co_ctrl = bool(phim & (KM.ControlModifier | KM.MetaModifier))
                sel_model = self.tbl_mon_hoc.selectionModel()
                model = self.tbl_mon_hoc.model()
                so_cot = self.tbl_mon_hoc.columnCount()
                SF = QItemSelectionModel.SelectionFlag

                def vung_dong(tu: int, den: int):
                    tren, duoi = sorted((tu, den))
                    return QItemSelection(model.index(tren, 0), model.index(duoi, so_cot - 1))

                if co_shift:
                    neo = self.dong_neo if self.dong_neo is not None else row
                    if self.dong_neo is None:
                        self.dong_neo = row
                    cach_chon = SF.Select if co_ctrl else SF.ClearAndSelect
                    sel_model.select(vung_dong(neo, row), cach_chon | SF.Rows)
                elif co_ctrl:
                    sel_model.select(vung_dong(row, row), SF.Toggle | SF.Rows)
                    self.dong_neo = row
                else:
                    # Click thường: chọn dòng này rồi để ô nhập xử lý tiếp (đặt con trỏ gõ chữ)
                    # Không dùng selectRow() vì nó đổi ô hiện hành và làm focus nhảy sang ô đầu dòng,
                    # khiến người dùng không gõ được vào ô vừa click
                    self.dong_neo = row
                    sel_model.select(vung_dong(row, row), SF.ClearAndSelect | SF.Rows)
                    if isinstance(obj, QLineEdit):
                        QTimer.singleShot(0, obj.setFocus)
                    return super().eventFilter(obj, event)

                # Shift/Ctrl chỉ để chọn dòng: bỏ con trỏ khỏi ô nhập để không còn viền focus gây rối
                self.tbl_mon_hoc.setFocus()
                return True
        return super().eventFilter(obj, event)

    def _lay_cac_dong_duoc_chon(self):
        """Trả về tập chỉ số các dòng đang được chọn"""
        return {idx.row() for idx in self.tbl_mon_hoc.selectedIndexes()}

    def _cap_nhat_giao_dien_chon(self, *_):
        """Tô sáng các ô nhập thuộc dòng đang chọn (vì ô nhập che mất màu chọn của bảng)"""
        dong_chon = self._lay_cac_dong_duoc_chon()
        for r in range(self.tbl_mon_hoc.rowCount()):
            for c in (0, 1, 2):
                w = self.tbl_mon_hoc.cellWidget(r, c)
                if w is None:
                    continue
                w.setProperty("chon", r in dong_chon)
                w.style().unpolish(w)
                w.style().polish(w)

    def _ket_noi_su_kien(self):
        """Kết nối các nút với hàm xử lý tương ứng"""
        self.btn_them_mon.clicked.connect(lambda: self.them_mon())
        self.btn_xoa_mon.clicked.connect(self.xoa_dong_duoc_chon)
        self.txt_gpa_muc_tieu.textChanged.connect(self.tinh_diem_can_dat)

    def _khoi_tao_du_lieu_mau(self):
        """Nạp danh sách môn học mẫu ban đầu"""
        ds_mau = [
            ("Toán cao cấp 1 (Calculus I)", 4, 9.2),
            ("Vật lý đại cương (Physics I)", 4, 8.4),
            ("Anh văn học thuật (English Comp)", 3, 7.8),
            ("Nhập môn lập trình (CS 101)", 3, 8.0),
            ("Triết học Mác - Lênin", 3, 6.8),
        ]
        for ten, tin_chi, diem in ds_mau:
            self.them_mon(ten, tin_chi, diem)

    def quy_doi_diem(self, diem_so: float):
        """
        Quy đổi chuẩn theo Quy chế đào tạo đại học (UEL / ĐHQG-HCM):
        | Xếp loại        | Thang 10       | Thang 4 số | Điểm chữ |
        | Xuất sắc        | 9.0 - 10.0     | 4.0        | A+       |
        | Giỏi            | 8.0 - cận 9.0  | 3.5        | A        |
        | Khá             | 7.0 - cận 8.0  | 3.0        | B+       |
        | Trung bình khá  | 6.0 - cận 7.0  | 2.5        | B        |
        | Trung bình      | 5.0 - cận 6.0  | 2.0        | C        |
        | Yếu             | 4.0 - cận 5.0  | 1.5        | D+       |
        | Kém             | 3.0 - cận 4.0  | 1.0        | D        |
        | Kém             | < 3.0          | 0.0        | F        |
        """
        if self.che_do_diem == "HE_10":
            if diem_so >= 9.0:
                return "A+", 4.0, "Xuất sắc"
            elif diem_so >= 8.0:
                return "A", 3.5, "Giỏi"
            elif diem_so >= 7.0:
                return "B+", 3.0, "Khá"
            elif diem_so >= 6.0:
                return "B", 2.5, "Trung bình khá"
            elif diem_so >= 5.0:
                return "C", 2.0, "Trung bình"
            elif diem_so >= 4.0:
                return "D+", 1.5, "Yếu"
            elif diem_so >= 3.0:
                return "D", 1.0, "Kém"
            else:
                return "F", 0.0, "Kém"
        else:
            # Nhập điểm hệ 4 trực tiếp
            if diem_so >= 3.8:
                return "A+", 4.0, "Xuất sắc"
            elif diem_so >= 3.4:
                return "A", 3.5, "Giỏi"
            elif diem_so >= 2.9:
                return "B+", 3.0, "Khá"
            elif diem_so >= 2.4:
                return "B", 2.5, "Trung bình khá"
            elif diem_so >= 1.9:
                return "C", 2.0, "Trung bình"
            elif diem_so >= 1.4:
                return "D+", 1.5, "Yếu"
            elif diem_so >= 0.9:
                return "D", 1.0, "Kém"
            else:
                return "F", 0.0, "Kém"

    def them_mon(self, ten: str = "", tin_chi: int = 3, diem_nhap: float = None):
        row = self.tbl_mon_hoc.rowCount()
        self.tbl_mon_hoc.insertRow(row)
        self.tbl_mon_hoc.setRowHeight(row, 56)

        # 1. Cột Tên môn học
        txt_ten = QLineEdit(ten)
        txt_ten.setPlaceholderText("Nhập tên môn học...")
        txt_ten.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #E1E8F3;
                border-radius: 9px;
                padding: 6px 12px;
                background-color: #FFFFFF;
                font-size: 13px;
                color: #111827;
            }
            QLineEdit:focus {
                border: 1.5px solid #2D7BF3;
                background-color: #FAFCFF;
            }
            QLineEdit[chon="true"] {
                border: 1.5px solid #2D7BF3;
                background-color: #EAF3FF;
            }
        """)
        self.tbl_mon_hoc.setCellWidget(row, 0, txt_ten)

        # 2. Cột Số tín chỉ
        txt_tin_chi = QLineEdit(str(tin_chi))
        txt_tin_chi.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        txt_tin_chi.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #E1E8F3;
                border-radius: 9px;
                padding: 6px;
                background-color: #FFFFFF;
                font-size: 13px;
                font-weight: 600;
                color: #111827;
            }
            QLineEdit:focus {
                border: 1.5px solid #2D7BF3;
            }
            QLineEdit[chon="true"] {
                border: 1.5px solid #2D7BF3;
                background-color: #EAF3FF;
            }
            QLineEdit[loi="true"] {
                border: 1.5px solid #D92D20;
                background-color: #FEF2F2;
            }
        """)
        self.tbl_mon_hoc.setCellWidget(row, 1, txt_tin_chi)

        # 3. Cột Điểm số
        str_diem = f"{diem_nhap:.1f}" if (diem_nhap is not None) else ""
        txt_score = QLineEdit(str_diem)
        txt_score.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        txt_score.setPlaceholderText(self._placeholder_diem())
        txt_score.setToolTip(self._goi_y_diem())
        txt_tin_chi.setToolTip(self._goi_y_tin_chi())
        txt_score.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #E1E8F3;
                border-radius: 9px;
                padding: 6px;
                background-color: #FFFFFF;
                font-size: 13px;
                font-weight: 700;
                color: #111827;
            }
            QLineEdit:focus {
                border: 1.5px solid #2D7BF3;
                background-color: #FAFCFF;
            }
            QLineEdit[chon="true"] {
                border: 1.5px solid #2D7BF3;
                background-color: #EAF3FF;
            }
            QLineEdit[loi="true"] {
                border: 1.5px solid #D92D20;
                background-color: #FEF2F2;
            }
        """)
        self.tbl_mon_hoc.setCellWidget(row, 2, txt_score)

        # 4. Cột Điểm chữ (Badge tự động nhảy)
        lbl_grade = QLabel("--")
        lbl_grade.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        lbl_grade.setStyleSheet("""
            QLabel {
                background-color: #F4F7FB;
                border: 1px solid #E1E8F3;
                border-radius: 7px;
                padding: 4px 8px;
                font-size: 13px;
                font-weight: 700;
                color: #4B5565;
            }
        """)
        self.tbl_mon_hoc.setCellWidget(row, 3, lbl_grade)

        # 5. Cột Thao tác (Nút xóa SVG)
        btn_xoa = QPushButton()
        path_trash = os.path.join(ICON_DIR, "trash-2_dark.svg")
        if os.path.exists(path_trash):
            btn_xoa.setIcon(QIcon(path_trash))
            btn_xoa.setIconSize(QSize(18, 18))
        else:
            btn_xoa.setText("🗑")

        btn_xoa.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn_xoa.setToolTip("Xóa môn học này")
        btn_xoa.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 6px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #EAF3FF;
            }
        """)
        btn_xoa.clicked.connect(lambda: self._xoa_mon_tai_widget(btn_xoa))
        self.tbl_mon_hoc.setCellWidget(row, 4, btn_xoa)

        # Bắt click trên các ô để chọn dòng (hỗ trợ Shift/Ctrl chọn nhiều dòng)
        for w in (txt_ten, txt_tin_chi, txt_score, lbl_grade):
            w.setProperty("o_trong_bang", True)
            w.installEventFilter(self)

        # Gán sự kiện cho các ô nhập
        txt_tin_chi.textChanged.connect(lambda: self._on_tc_changed(row))
        txt_score.textChanged.connect(lambda: self._on_score_text_changed(row))
        # Rời khỏi ô (hoặc bấm Enter) mà dữ liệu sai thì hiện hộp thoại báo lỗi
        txt_tin_chi.editingFinished.connect(lambda: self._bao_loi_o_nhap(txt_tin_chi))
        txt_score.editingFinished.connect(lambda: self._bao_loi_o_nhap(txt_score))

        # Kích hoạt tính toán ban đầu
        self._on_score_text_changed(row)

    # ------------------------------------------------------------------
    # Kiểm tra dữ liệu nhập (trả về (hop_le, thong_bao) theo CONVENTION)
    # ------------------------------------------------------------------
    DIEM_TOI_DA = {"HE_10": 10.0, "HE_4": 4.0}
    TIN_CHI_TOI_DA = 10

    @staticmethod
    def _doc_so(text: str):
        """Đổi chuỗi sang số thực (chấp nhận dấu phẩy). Trả về None nếu không phải số hữu hạn"""
        try:
            val = float(text.strip().replace(",", "."))
        except ValueError:
            return None
        return val if math.isfinite(val) else None

    def kiem_tra_diem(self, text: str, che_do: str = None):
        """Kiểm tra điểm số nhập vào có nằm trong thang điểm đang chọn không. Ô trống là hợp lệ"""
        che_do = che_do or self.che_do_diem
        if not text.strip():
            return True, ""
        val = self._doc_so(text)
        ten_he = "10" if che_do == "HE_10" else "4"
        toi_da = self.DIEM_TOI_DA[che_do]
        if val is None:
            return False, f"Điểm phải là một số, ví dụ {'8.5' if che_do == 'HE_10' else '3.5'}."
        if val < 0 or val > toi_da:
            return False, (f"Điểm thang {ten_he} chỉ được từ 0 đến {toi_da:g}, "
                           f"nhưng bạn đã nhập {val:g}.")
        return True, ""

    def kiem_tra_tin_chi(self, text: str):
        """Kiểm tra số tín chỉ: là số, lớn hơn 0 và không vượt quá TIN_CHI_TOI_DA"""
        if not text.strip():
            return False, "Số tín chỉ không được để trống."
        val = self._doc_so(text)
        if val is None:
            return False, "Số tín chỉ phải là một số, ví dụ 3."
        if val <= 0 or val > self.TIN_CHI_TOI_DA:
            return False, (f"Số tín chỉ phải lớn hơn 0 và tối đa {self.TIN_CHI_TOI_DA}, "
                           f"nhưng bạn đã nhập {val:g}.")
        return True, ""

    def _goi_y_diem(self) -> str:
        toi_da = self.DIEM_TOI_DA[self.che_do_diem]
        ten_he = "10" if self.che_do_diem == "HE_10" else "4"
        return f"Nhập điểm từ 0 đến {toi_da:g} (thang {ten_he})"

    def _goi_y_tin_chi(self) -> str:
        return f"Nhập số tín chỉ từ 1 đến {self.TIN_CHI_TOI_DA}"

    def _placeholder_diem(self) -> str:
        return "VD: 8.5 (0 - 10)" if self.che_do_diem == "HE_10" else "VD: 3.5 (0 - 4)"

    def _cap_nhat_goi_y_theo_he(self):
        """Cập nhật tiêu đề cột, placeholder và tooltip theo thang điểm đang chọn để người dùng biết mức tối đa"""
        he10 = self.che_do_diem == "HE_10"
        toi_da = self.DIEM_TOI_DA[self.che_do_diem]
        self.tbl_mon_hoc.horizontalHeaderItem(2).setText(
            f"Điểm số (Hệ {'10' if he10 else '4'}: 0 - {toi_da:g})")
        for r in range(self.tbl_mon_hoc.rowCount()):
            txt_score = self.tbl_mon_hoc.cellWidget(r, 2)
            if txt_score:
                txt_score.setPlaceholderText(self._placeholder_diem())
        self.txt_gpa_muc_tieu.setPlaceholderText(
            f"Ví dụ: {'8.0' if he10 else '3.20'} (tối đa {toi_da:g})")
        self.txt_gpa_muc_tieu.setToolTip(
            f"Nhập GPA mong muốn theo thang {'10' if he10 else '4'}, từ 0 đến {toi_da:g}.\n"
            "Để trống ô điểm của môn chưa học để tính điểm cần đạt cho môn đó.")

    def _dat_loi(self, o: QLineEdit, thong_bao: str, goi_y: str):
        """Đánh dấu ô nhập sai (viền đỏ + tooltip nêu lỗi), hoặc bỏ đánh dấu nếu thong_bao rỗng"""
        loi = bool(thong_bao)
        tooltip = thong_bao or goi_y
        if o.property("loi") == loi and o.toolTip() == tooltip:
            return
        o.setProperty("loi", loi)
        o.setProperty("thong_bao_loi", thong_bao)
        o.setToolTip(tooltip)
        o.style().unpolish(o)
        o.style().polish(o)

    def _bao_loi_o_nhap(self, o: QLineEdit):
        """Hiện hộp thoại báo lỗi khi người dùng rời khỏi ô nhập đang sai"""
        thong_bao = o.property("thong_bao_loi")
        if not thong_bao or self._dang_bao_loi:
            return
        self._dang_bao_loi = True
        try:
            self._thong_bao("Dữ liệu chưa hợp lệ", thong_bao)
        finally:
            self._dang_bao_loi = False

    def _on_score_text_changed(self, row: int):
        """Khi sinh viên nhập điểm, tự động kiểm tra, cập nhật Grade và GPA tức thời"""
        if row >= self.tbl_mon_hoc.rowCount():
            return

        txt_score = self.tbl_mon_hoc.cellWidget(row, 2)
        lbl_grade = self.tbl_mon_hoc.cellWidget(row, 3)

        if not (txt_score and lbl_grade):
            return

        text = txt_score.text().strip().replace(",", ".")
        hop_le, thong_bao = self.kiem_tra_diem(text)
        self._dat_loi(txt_score, thong_bao, self._goi_y_diem())

        if not text:
            # Chưa nhập điểm
            lbl_grade.setText("--")
            lbl_grade.setProperty("diem_he_4", None)
            lbl_grade.setStyleSheet("""
                background-color: #F4F7FB;
                border: 1px solid #E1E8F3;
                border-radius: 7px;
                padding: 4px 8px;
                font-size: 13px;
                font-weight: 600;
                color: #9CA3AF;
            """)
        elif not hop_le:
            lbl_grade.setText("Lỗi")
            lbl_grade.setProperty("diem_he_4", None)
            lbl_grade.setStyleSheet("""
                background-color: #FEF2F2;
                border: 1.5px solid #FCA5A5;
                border-radius: 7px;
                padding: 4px 8px;
                font-size: 13px;
                font-weight: 700;
                color: #D92D20;
            """)
        else:
            diem_so = float(text)
            grade_chu, diem_qd, _ = self.quy_doi_diem(diem_so)
            lbl_grade.setText(grade_chu)
            lbl_grade.setProperty("diem_he_4", diem_qd)

            # Màu sắc badge chữ cái điểm
            if "A" in grade_chu:
                badge_bg, badge_border, badge_color = "#EAF3FF", "#2D7BF3", "#1E5FCC"
            elif "B" in grade_chu:
                badge_bg, badge_border, badge_color = "#EFF6FF", "#93C5FD", "#1E40AF"
            elif "C" in grade_chu:
                badge_bg, badge_border, badge_color = "#FFFBEB", "#FCD34D", "#92400E"
            elif "D" in grade_chu:
                badge_bg, badge_border, badge_color = "#FFF7ED", "#FDBA74", "#9A3412"
            else:
                badge_bg, badge_border, badge_color = "#FEF2F2", "#FCA5A5", "#991B1B"

            lbl_grade.setStyleSheet(f"""
                background-color: {badge_bg};
                border: 1.5px solid {badge_border};
                border-radius: 7px;
                padding: 4px 8px;
                font-size: 13px;
                font-weight: 800;
                color: {badge_color};
            """)

        self.tinh_gpa_hien_tai()

    def _on_tc_changed(self, row: int):
        """Khi số tín chỉ thay đổi thì kiểm tra rồi tính lại GPA"""
        if 0 <= row < self.tbl_mon_hoc.rowCount():
            txt_tc = self.tbl_mon_hoc.cellWidget(row, 1)
            if txt_tc:
                _, thong_bao = self.kiem_tra_tin_chi(txt_tc.text())
                self._dat_loi(txt_tc, thong_bao, self._goi_y_tin_chi())
        self.tinh_gpa_hien_tai()

    def _xoa_mon_tai_widget(self, btn):
        """Xóa hàng chứa nút bấm được click"""
        for r in range(self.tbl_mon_hoc.rowCount()):
            if self.tbl_mon_hoc.cellWidget(r, 4) == btn:
                self.xoa_mon(r)
                break

    def xoa_mon(self, row_index: int):
        """Xóa môn học tại chỉ số dòng row_index"""
        if 0 <= row_index < self.tbl_mon_hoc.rowCount():
            self.tbl_mon_hoc.removeRow(row_index)
            self._cap_nhat_lai_ket_noi()
            self.tinh_gpa_hien_tai()

    def _tao_hop_thoai(self, tieu_de: str, noi_dung: str, chi_tiet: str = "",
                       ten_icon: str = ""):
        """Tạo QMessageBox đã áp theme chung của ứng dụng (bo tròn, xanh dương, chữ đậm)"""
        hop = QMessageBox(self)
        hop.setWindowTitle(tieu_de)
        hop.setText(noi_dung)
        if chi_tiet:
            hop.setInformativeText(chi_tiet)

        path = os.path.join(ICON_DIR, ten_icon) if ten_icon else ""
        if path and os.path.exists(path):
            hop.setIconPixmap(QIcon(path).pixmap(QSize(36, 36)))
        else:
            hop.setIcon(QMessageBox.Icon.NoIcon)

        hop.setStyleSheet("""
            QMessageBox { background-color: #FFFFFF; }
            QMessageBox QLabel { color: #16181E; font-size: 13px; background: transparent; }
            QMessageBox QLabel#qt_msgbox_label { font-size: 15px; font-weight: 700; }
            QMessageBox QLabel#qt_msgbox_informativelabel { color: #4B5565; font-weight: 500; }
            QMessageBox QPushButton {
                background-color: #FFFFFF; border: 1.5px solid #E1E8F3; border-radius: 20px;
                color: #16181E; font-size: 13px; font-weight: 700;
                min-width: 110px; min-height: 40px; padding: 0 20px;
            }
            QMessageBox QPushButton:hover { background-color: #EAF3FF; border-color: #2D7BF3; }
            QMessageBox QPushButton#btn_dong_y {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2D7BF3, stop:1 #5B9BF8);
                border: none; color: #FFFFFF;
            }
            QMessageBox QPushButton#btn_dong_y:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1F6BE0, stop:1 #4A8FF6);
            }
        """)
        return hop

    def _hoi_xac_nhan(self, tieu_de: str, noi_dung: str, chi_tiet: str,
                      ten_nut_dong_y: str, ten_icon: str = "") -> bool:
        """Hộp thoại hỏi xác nhận 2 nút tiếng Việt. Trả về True nếu người dùng đồng ý"""
        hop = self._tao_hop_thoai(tieu_de, noi_dung, chi_tiet, ten_icon)
        btn_huy = hop.addButton("Hủy", QMessageBox.ButtonRole.RejectRole)
        btn_dong_y = hop.addButton(ten_nut_dong_y, QMessageBox.ButtonRole.AcceptRole)
        btn_dong_y.setObjectName("btn_dong_y")
        btn_dong_y.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn_huy.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        hop.setDefaultButton(btn_huy)  # Enter mặc định là Hủy cho an toàn
        hop.setEscapeButton(btn_huy)
        hop.exec()
        return hop.clickedButton() is btn_dong_y

    def _thong_bao(self, tieu_de: str, noi_dung: str, chi_tiet: str = ""):
        """Hộp thoại thông báo một nút OK"""
        hop = self._tao_hop_thoai(tieu_de, noi_dung, chi_tiet)
        btn_ok = hop.addButton("Đã hiểu", QMessageBox.ButtonRole.AcceptRole)
        btn_ok.setObjectName("btn_dong_y")
        btn_ok.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        hop.exec()

    def xoa_dong_duoc_chon(self):
        """Xóa tất cả các dòng đang được chọn trong bảng (hỗ trợ chọn nhiều dòng bằng Shift)"""
        dong_chon = sorted(self._lay_cac_dong_duoc_chon(), reverse=True)
        if not dong_chon:
            self._thong_bao(
                "Chưa chọn môn học", "Bạn chưa chọn môn học nào để xóa.",
                "Bấm vào một dòng để chọn. Giữ Shift để chọn một dãy dòng, "
                "giữ Ctrl (⌘ trên Mac) để chọn từng dòng rời.")
            return

        if len(dong_chon) > 1:
            dong_y = self._hoi_xac_nhan(
                "Xác nhận xóa", f"Xóa {len(dong_chon)} môn học đã chọn?",
                "Thao tác này không thể hoàn tác.", "Xóa", "trash-2_dark.svg")
            if not dong_y:
                return

        # Xóa từ dưới lên để chỉ số các dòng phía trên không bị lệch
        for r in dong_chon:
            self.tbl_mon_hoc.removeRow(r)
        self.dong_neo = None
        self.tbl_mon_hoc.clearSelection()
        self._cap_nhat_lai_ket_noi()
        self.tinh_gpa_hien_tai()

    def _cap_nhat_lai_ket_noi(self):
        """Kết nối lại sự kiện index sau khi dòng bị xóa"""
        for r in range(self.tbl_mon_hoc.rowCount()):
            txt_tc = self.tbl_mon_hoc.cellWidget(r, 1)
            txt_sc = self.tbl_mon_hoc.cellWidget(r, 2)
            if txt_tc and txt_sc:
                try:
                    txt_tc.textChanged.disconnect()
                except Exception:
                    pass
                try:
                    txt_sc.textChanged.disconnect()
                except Exception:
                    pass
                current_r = r
                txt_tc.textChanged.connect(lambda _, row=current_r: self._on_tc_changed(row))
                txt_sc.textChanged.connect(lambda _, row=current_r: self._on_score_text_changed(row))

    def lay_du_lieu_mon(self):
        """
        Đọc và trả về danh sách các môn học theo chuẩn CONVENTION.md:
        [{"ten": "Toan", "tin_chi": 3, "diem": 3.5}, ...]
        Nếu môn chưa nhập điểm, 'diem' sẽ là None.
        """
        ds_mon = []
        for r in range(self.tbl_mon_hoc.rowCount()):
            txt_ten = self.tbl_mon_hoc.cellWidget(r, 0)
            txt_tc = self.tbl_mon_hoc.cellWidget(r, 1)
            txt_sc = self.tbl_mon_hoc.cellWidget(r, 2)
            lbl_grade = self.tbl_mon_hoc.cellWidget(r, 3)

            ten = txt_ten.text().strip() if txt_ten else ""
            hop_le_tc, _ = self.kiem_tra_tin_chi(txt_tc.text()) if txt_tc else (False, "")
            tin_chi = self._doc_so(txt_tc.text()) if hop_le_tc else 0.0

            diem_qd = None
            if txt_sc and txt_sc.text().strip() and lbl_grade:
                diem_qd = lbl_grade.property("diem_he_4")

            ds_mon.append({
                "ten": ten,
                "tin_chi": tin_chi,
                "diem": diem_qd
            })
        return ds_mon

    # ------------------------------------------------------------------
    # Hằng số dùng chung
    # ------------------------------------------------------------------
    # (ngưỡng GPA, chỉ số chip thang điểm, xếp loại, lời động viên)
    BAC_GPA = [
        (3.6, 0, "Xuất sắc (A+)", "Phong độ cực đỉnh, tiếp tục phát huy nhé!"),
        (3.2, 1, "Giỏi (A)", "Kết quả rất tốt, hãy tiếp tục duy trì nhé!"),
        (2.85, 2, "Khá (B+)", "Cố gắng thêm chút nữa để chạm mốc Giỏi nhé!"),
        (2.5, 3, "Khá (B)", "Cố gắng thêm chút nữa để chạm mốc Giỏi nhé!"),
        (2.0, 4, "Trung bình (C)", "Cần tập trung học tập để cải thiện thứ hạng!"),
        (1.5, 5, "Yếu (D+)", "Cần chú ý lập kế hoạch học tập nghiêm túc!"),
        (1.0, 6, "Kém (D)", "Cần chú ý lập kế hoạch học tập nghiêm túc!"),
        (0.0, 7, "Kém (F)", "Cần chú ý lập kế hoạch học tập nghiêm túc!"),
    ]
    # (điểm hệ 4, điểm chữ, cận dưới thang 10) - dùng cho GPA mục tiêu
    BANG_QUY_DOI = [
        (4.0, "A+", 9.0), (3.5, "A", 8.0), (3.0, "B+", 7.0), (2.5, "B", 6.0),
        (2.0, "C", 5.0), (1.5, "D+", 4.0), (1.0, "D", 3.0), (0.0, "F", 0.0),
    ]
    # Màu chữ cái từng chip khi KHÔNG được chọn
    MAU_CHU_CHIP = ["#2D7BF3", "#2D7BF3", "#3F83E8", "#5A8FD6",
                    "#6E7F99", "#69758C", "#5B6578", "#16181E"]

    def _cai_dat_cong_thuc(self):
        """Hiển thị công thức GPA dạng phân số (rich text)"""
        he = "10" if self.che_do_diem == "HE_10" else "4"
        html = (
            '<table align="center" cellspacing="0" cellpadding="0"><tr>'
            '<td rowspan="3" valign="middle">GPA&nbsp;=&nbsp;&nbsp;</td>'
            f'<td align="center">∑ (Điểm hệ {he} × Số tín chỉ)</td></tr>'
            '<tr><td height="1" bgcolor="#FFFFFF" style="font-size:1px;"><span style="font-size:1px;">&nbsp;</span></td></tr>'
            '<tr><td align="center">∑ Số tín chỉ</td></tr></table>'
        )
        self.lbl_cong_thuc.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.lbl_cong_thuc.setWordWrap(False)
        self.lbl_cong_thuc.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lbl_cong_thuc.setText(html)
        self.frame_tip.setMinimumHeight(68)

        # Căn công thức vào chính giữa ô: icon bên trái được cân bằng bằng một khoảng trống
        # cùng kích thước bên phải, nhãn công thức chiếm phần còn lại ở giữa
        if not getattr(self, "_da_can_giua_cong_thuc", False):
            lay = self.frame_tip_layout
            lay.takeAt(lay.count() - 1)  # bỏ spacer phải
            lay.takeAt(0)                # bỏ spacer trái
            lay.setStretchFactor(self.lbl_cong_thuc, 1)
            self.lbl_cong_thuc.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
            lay.addSpacing(self.icon_info.maximumWidth())
            self._da_can_giua_cong_thuc = True

    def _cap_nhat_chip_chon(self, chi_so):
        """Tô sáng chip thang điểm tương ứng với GPA (chi_so = None: không chọn)"""
        for i in range(8):
            box = getattr(self, f"scale_box_{i + 1}")
            lbl_g = getattr(self, f"lbl_g_{i + 1}")
            lbl_p = getattr(self, f"lbl_p_{i + 1}")
            lbl_t = getattr(self, f"lbl_t_{i + 1}")
            if i == chi_so:
                box.setStyleSheet(
                    f"QFrame#scale_box_{i + 1} {{ background-color: qlineargradient("
                    "x1:0, y1:0, x2:1, y2:1, stop:0 #2D7BF3, stop:1 #5B9BF8); "
                    "border: none; border-radius: 16px; }")
                lbl_g.setStyleSheet("font-weight: 800; font-size: 14px; color: #FFFFFF;")
                lbl_p.setStyleSheet("font-size: 11px; font-weight: 700; color: #FFFFFF;")
                lbl_t.setStyleSheet("font-size: 10px; color: #DCEBFF;")
            else:
                box.setStyleSheet(
                    f"QFrame#scale_box_{i + 1} {{ background-color: #F4F7FB; "
                    "border: 1px solid #E6ECF5; border-radius: 16px; }")
                lbl_g.setStyleSheet(
                    f"font-weight: 800; font-size: 14px; color: {self.MAU_CHU_CHIP[i]};")
                lbl_p.setStyleSheet("font-size: 11px; font-weight: 600; color: #16181E;")
                lbl_t.setStyleSheet("font-size: 10px; color: #8A93A5;")

    @staticmethod
    def tinh_gpa_theo_diem(ds_diem):
        """
        Tính GPA theo trung bình có trọng số tín chỉ.
        ds_diem: danh sách (tin_chi, diem) chỉ gồm các môn đã có điểm.
        Trả về (tong_tin_chi, tong_diem, gpa), không đụng vào widget.
        """
        tong_tc = sum(tc for tc, _ in ds_diem if tc > 0)
        tong_diem = sum(tc * diem for tc, diem in ds_diem if tc > 0)
        gpa = tong_diem / tong_tc if tong_tc > 0 else 0.0
        return tong_tc, tong_diem, gpa

    def _lay_diem_goc_theo_he_dang_chon(self):
        """Lấy (tín chỉ, điểm đang nhập theo hệ hiện tại) của các môn đã có điểm hợp lệ"""
        ds = []
        for r in range(self.tbl_mon_hoc.rowCount()):
            txt_tc = self.tbl_mon_hoc.cellWidget(r, 1)
            txt_sc = self.tbl_mon_hoc.cellWidget(r, 2)
            lbl_grade = self.tbl_mon_hoc.cellWidget(r, 3)
            if not (txt_tc and txt_sc and lbl_grade):
                continue
            if lbl_grade.property("diem_he_4") is None:
                continue
            hop_le_tc, _ = self.kiem_tra_tin_chi(txt_tc.text())
            diem = self._doc_so(txt_sc.text())
            if not hop_le_tc or diem is None:
                continue
            ds.append((self._doc_so(txt_tc.text()), diem))
        return ds

    def tinh_gpa_hien_tai(self):
        """Tính tổng tín chỉ, tổng điểm, GPA và tô sáng chip thang điểm tương ứng"""
        ds_mon = self.lay_du_lieu_mon()
        tong_tc_toan_bo = sum(mon["tin_chi"] for mon in ds_mon)

        # GPA hệ 4 dùng để xếp loại và tính điểm cần đạt
        ds_he_4 = [(m["tin_chi"], m["diem"]) for m in ds_mon if m["diem"] is not None]
        tong_tc_co_diem, tong_diem_he_4, gpa = self.tinh_gpa_theo_diem(ds_he_4)

        # GPA hiển thị: theo hệ người dùng đang chọn
        if self.che_do_diem == "HE_10":
            _, tong_diem_hien_thi, gpa_hien_thi = self.tinh_gpa_theo_diem(
                self._lay_diem_goc_theo_he_dang_chon())
            self.lbl_txt_tong_diem.setText("Tổng điểm tích lũy (Hệ 10)")
            self.lbl_thang_diem.setText("10.00")
        else:
            tong_diem_hien_thi, gpa_hien_thi = tong_diem_he_4, gpa
            self.lbl_txt_tong_diem.setText("Tổng điểm tích lũy (Hệ 4)")
            self.lbl_thang_diem.setText("4.00")

        tc_text = str(int(tong_tc_toan_bo)) if float(tong_tc_toan_bo).is_integer() else f"{tong_tc_toan_bo:.1f}"
        self.lbl_tong_tin_chi.setText(tc_text)
        self.lbl_tong_diem.setText(f"{tong_diem_hien_thi:.2f}")
        self.lbl_gpa_hien_tai.setText(f"{gpa_hien_thi:.2f}")

        if tong_tc_co_diem == 0:
            self.lbl_trang_thai_gpa.setText("Chưa có điểm")
            self.lbl_dong_vien.setText("Nhập điểm các môn để xem GPA của bạn.")
            self._cap_nhat_chip_chon(None)
        else:
            for nguong, chi_so, xep_loai, loi in self.BAC_GPA:
                if gpa >= nguong:
                    self.lbl_trang_thai_gpa.setText(f"Xếp loại: {xep_loai}")
                    self.lbl_dong_vien.setText(loi)
                    self._cap_nhat_chip_chon(chi_so)
                    break

        self.tinh_diem_can_dat()
        return gpa

    def _hien_thi_muc_tieu(self, text: str, mau: str = "#16181E"):
        self.lbl_diem_can_dat.setText(text)
        self.lbl_diem_can_dat.setStyleSheet(f"color: {mau}; font-size: 12px; font-weight: 700;")

    def _he10_sang_he4(self, diem10: float) -> float:
        """Đổi điểm thang 10 sang thang 4 theo bảng quy chế (lấy theo mốc cận dưới)"""
        for diem4, _, can_duoi in self.BANG_QUY_DOI:
            if diem10 >= can_duoi:
                return diem4
        return 0.0

    def tinh_diem_can_dat(self):
        """
        GPA mục tiêu được hiểu theo thang điểm đang chọn (Hệ 10: 0-10, Hệ 4: 0-4).
        Tính điểm trung bình tối thiểu cần đạt ở các môn CHƯA có điểm (ô điểm để trống),
        kết quả hiển thị cùng thang điểm với mục tiêu.
        """
        he10 = self.che_do_diem == "HE_10"
        toi_da = self.DIEM_TOI_DA[self.che_do_diem]
        ten_he = "10" if he10 else "4"

        muc_tieu = self._doc_so(self.txt_gpa_muc_tieu.text())
        if not self.txt_gpa_muc_tieu.text().strip():
            self._hien_thi_muc_tieu("Điểm cần đạt các môn còn lại: --", "#4B5565")
            return
        if muc_tieu is None:
            self._hien_thi_muc_tieu("GPA mục tiêu phải là số!", "#D92D20")
            return
        if muc_tieu < 0 or muc_tieu > toi_da:
            self._hien_thi_muc_tieu(
                f"GPA mục tiêu thang {ten_he} chỉ được từ 0 đến {toi_da:g}.", "#D92D20")
            return

        ds_mon = self.lay_du_lieu_mon()
        tc_chua = sum(m["tin_chi"] for m in ds_mon if m["diem"] is None)
        if he10:
            ds_co_diem = self._lay_diem_goc_theo_he_dang_chon()
        else:
            ds_co_diem = [(m["tin_chi"], m["diem"]) for m in ds_mon if m["diem"] is not None]
        tc_co_diem, tong_diem, _ = self.tinh_gpa_theo_diem(ds_co_diem)
        tong_tc = tc_co_diem + tc_chua

        if tong_tc <= 0:
            self._hien_thi_muc_tieu("Hãy thêm môn học để tính điểm cần đạt.", "#4B5565")
            return

        if tc_chua == 0:
            gpa = tong_diem / tong_tc
            if gpa >= muc_tieu:
                self._hien_thi_muc_tieu(
                    f"Đã đạt mục tiêu: GPA hiện tại {gpa:.2f} ≥ {muc_tieu:.2f}", "#1E5FCC")
            else:
                self._hien_thi_muc_tieu(
                    f"Chưa đạt mục tiêu: còn thiếu {muc_tieu - gpa:.2f} điểm. "
                    "Thêm môn mới và để trống ô điểm để xem điểm cần đạt.", "#4B5565")
            return

        can_dat = (muc_tieu * tong_tc - tong_diem) / tc_chua
        tc_chua_txt = f"{tc_chua:g}"
        if can_dat > toi_da + 1e-9:
            self._hien_thi_muc_tieu(
                f"Không khả thi: cần TB {can_dat:.2f} > {toi_da:.2f} "
                f"cho {tc_chua_txt} tín chỉ còn lại", "#D92D20")
        elif can_dat <= 0:
            self._hien_thi_muc_tieu(
                "Chắc chắn đạt mục tiêu, kể cả khi các môn còn lại điểm thấp.", "#1E5FCC")
        elif he10:
            hang = "F"
            for _, chu, can_duoi in self.BANG_QUY_DOI:
                if can_dat >= can_duoi - 1e-9:
                    hang = chu
                    break
            self._hien_thi_muc_tieu(
                f"Cần TB tối thiểu {can_dat:.2f}/10.00 (≈ hạng {hang}) "
                f"cho {tc_chua_txt} tín chỉ còn lại", "#16181E")
        else:
            hang, can_duoi = "A+", 9.0
            for diem4, chu, lo in reversed(self.BANG_QUY_DOI):
                if diem4 >= can_dat - 1e-9:
                    hang, can_duoi = chu, lo
                    break
            self._hien_thi_muc_tieu(
                f"Cần TB tối thiểu {can_dat:.2f}/4.00 (≈ hạng {hang}, từ {can_duoi:.1f}/10) "
                f"cho {tc_chua_txt} tín chỉ còn lại", "#16181E")

    def _cap_nhat_card_scale_he_10(self):
        """Cập nhật ghi chú thang điểm quy đổi theo thang 10 chuẩn trường"""
        self.lbl_p_1.setText("4.0 (≥9.0)")
        self.lbl_p_2.setText("3.5 (8.0-8.9)")
        self.lbl_p_3.setText("3.0 (7.0-7.9)")
        self.lbl_p_4.setText("2.5 (6.0-6.9)")
        self.lbl_p_5.setText("2.0 (5.0-5.9)")
        self.lbl_p_6.setText("1.5 (4.0-4.9)")
        self.lbl_p_7.setText("1.0 (3.0-3.9)")
        self.lbl_p_8.setText("0.0 (<3.0)")

    def _cap_nhat_card_scale_he_4(self):
        """Cập nhật ghi chú thang điểm quy đổi khi chọn hệ 4"""
        self.lbl_p_1.setText("4.0 (≥3.8)")
        self.lbl_p_2.setText("3.5 (3.4-3.7)")
        self.lbl_p_3.setText("3.0 (2.9-3.3)")
        self.lbl_p_4.setText("2.5 (2.4-2.8)")
        self.lbl_p_5.setText("2.0 (1.9-2.3)")
        self.lbl_p_6.setText("1.5 (1.4-1.8)")
        self.lbl_p_7.setText("1.0 (0.9-1.3)")
        self.lbl_p_8.setText("0.0 (<0.9)")