import os
import sys
import importlib
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTableWidgetItem, QLineEdit, 
    QPushButton, QLabel, QHBoxLayout, QMessageBox, QHeaderView, QButtonGroup
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize

# Load module UI cùng thư mục (xử lý tiền tố số 01_ theo convention)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
ICON_DIR = os.path.join(ROOT_DIR, "Images", "icons")

ui_module = importlib.import_module("01_MainScreen")
Ui_MainScreen = ui_module.Ui_MainScreen


class MainScreen_Ext(QMainWindow, Ui_MainScreen):
    """
    Class xử lý logic cho màn hình chính GPA Calculator
    Tuân thủ quy chuẩn CONVENTION.md và Quy chế đào tạo đại học.
    Tự động tính toán tức thời (real-time), không cần bấm nút tính.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
        # Biến trạng thái: "HE_10" hoặc "HE_4"
        self.che_do_diem = "HE_10"
        
        self._cai_dat_icon_svg()
        self._cai_dat_nhom_nut_he()
        self._cai_dat_bang()
        self._ket_noi_su_kien()
        self._khoi_tao_du_lieu_mau()
        self.tinh_gpa_hien_tai()

    def _cai_dat_icon_svg(self):
        """Tải các icon SVG vector sắc nét vào giao diện"""
        def set_svg_label(label: QLabel, svg_name: str, width: int = 22, height: int = 22):
            path = os.path.join(ICON_DIR, svg_name)
            if os.path.exists(path):
                pix = QPixmap(path).scaled(width, height, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
                label.setPixmap(pix)

        # Header icon
        set_svg_label(self.lbl_header_icon, "calculator.svg", 26, 26)
        
        # Stat icons bên thẻ phải
        set_svg_label(self.icon_credits, "academic.svg", 18, 18)
        set_svg_label(self.icon_points, "star.svg", 18, 18)
        set_svg_label(self.icon_scale, "chart.svg", 18, 18)
        set_svg_label(self.icon_info, "info.svg", 16, 16)
        
        # Nút thêm môn
        path_plus = os.path.join(ICON_DIR, "plus.svg")
        if os.path.exists(path_plus):
            self.btn_them_mon.setIcon(QIcon(path_plus))
            self.btn_them_mon.setIconSize(QSize(14, 14))

    def _cai_dat_nhom_nut_he(self):
        """Tạo nhóm nút chuyển đổi Hệ 10 và Hệ 4 kiểu pill switch"""
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
            self.tbl_mon_hoc.horizontalHeaderItem(2).setText("Điểm số (Hệ 10)")
            self.lbl_scale_title.setText("Thang Điểm Quy Đổi (Theo Thang 10)")
            self._cap_nhat_card_scale_he_10()
        else:
            self.tbl_mon_hoc.horizontalHeaderItem(2).setText("Điểm số (Hệ 4)")
            self.lbl_scale_title.setText("Thang Điểm Quy Đổi (Theo Thang 4)")
            self._cap_nhat_card_scale_he_4()
            
        # Tự động quy đổi giá trị trong các ô điểm hiện có
        for r in range(self.tbl_mon_hoc.rowCount()):
            txt_score = self.tbl_mon_hoc.cellWidget(r, 2)
            if txt_score and txt_score.text().strip():
                try:
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

    def _cai_dat_bang(self):
        """Cấu hình bảng tbl_mon_hoc 5 cột chuẩn"""
        header = self.tbl_mon_hoc.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)         # Tên môn học
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)           # Số tín chỉ
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)           # Điểm số
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)           # Điểm chữ
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)           # Thao tác
        
        self.tbl_mon_hoc.setColumnWidth(1, 130)  # Số tín chỉ
        self.tbl_mon_hoc.setColumnWidth(2, 160)  # Điểm số
        self.tbl_mon_hoc.setColumnWidth(3, 130)  # Điểm chữ
        self.tbl_mon_hoc.setColumnWidth(4, 90)   # Thao tác
        
        self.tbl_mon_hoc.verticalHeader().setVisible(False)
        self.tbl_mon_hoc.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl_mon_hoc.setShowGrid(False)

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
        """
        Thêm một dòng môn học vào bảng:
        Cột 0: Tên môn học (QLineEdit)
        Cột 1: Số tín chỉ (QLineEdit)
        Cột 2: Điểm số (QLineEdit)
        Cột 3: Điểm chữ (QLabel tự động nhảy)
        Cột 4: Thao tác (QPushButton xóa có icon SVG)
        """
        row = self.tbl_mon_hoc.rowCount()
        self.tbl_mon_hoc.insertRow(row)
        self.tbl_mon_hoc.setRowHeight(row, 56)

        # 1. Cột Tên môn học
        txt_ten = QLineEdit(ten)
        txt_ten.setPlaceholderText("Nhập tên môn học...")
        txt_ten.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #E5E7EB;
                border-radius: 9px;
                padding: 6px 12px;
                background-color: #FFFFFF;
                font-size: 13px;
                color: #111827;
            }
            QLineEdit:focus {
                border: 1.5px solid #ADBF15;
                background-color: #FCFCF7;
            }
        """)
        self.tbl_mon_hoc.setCellWidget(row, 0, txt_ten)

        # 2. Cột Số tín chỉ
        txt_tin_chi = QLineEdit(str(tin_chi))
        txt_tin_chi.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        txt_tin_chi.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #E5E7EB;
                border-radius: 9px;
                padding: 6px;
                background-color: #FFFFFF;
                font-size: 13px;
                font-weight: 600;
                color: #111827;
            }
            QLineEdit:focus {
                border: 1.5px solid #ADBF15;
            }
        """)
        self.tbl_mon_hoc.setCellWidget(row, 1, txt_tin_chi)

        # 3. Cột Điểm số
        str_diem = f"{diem_nhap:.1f}" if (diem_nhap is not None) else ""
        txt_score = QLineEdit(str_diem)
        txt_score.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        txt_score.setPlaceholderText("VD: 8.5" if self.che_do_diem == "HE_10" else "VD: 3.5")
        txt_score.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #E5E7EB;
                border-radius: 9px;
                padding: 6px;
                background-color: #FFFFFF;
                font-size: 13px;
                font-weight: 700;
                color: #111827;
            }
            QLineEdit:focus {
                border: 1.5px solid #ADBF15;
                background-color: #FCFCF7;
            }
        """)
        self.tbl_mon_hoc.setCellWidget(row, 2, txt_score)

        # 4. Cột Điểm chữ (Badge tự động nhảy)
        lbl_grade = QLabel("--")
        lbl_grade.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        lbl_grade.setStyleSheet("""
            QLabel {
                background-color: #F8F8EB;
                border: 1px solid #E5E7D8;
                border-radius: 7px;
                padding: 4px 8px;
                font-size: 13px;
                font-weight: 700;
                color: #6B7280;
            }
        """)
        self.tbl_mon_hoc.setCellWidget(row, 3, lbl_grade)

        # 5. Cột Thao tác (Nút xóa SVG)
        btn_xoa = QPushButton()
        path_trash = os.path.join(ICON_DIR, "trash.svg")
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
                background-color: #FEE2E2;
            }
        """)
        btn_xoa.clicked.connect(lambda: self._xoa_mon_tai_widget(btn_xoa))
        self.tbl_mon_hoc.setCellWidget(row, 4, btn_xoa)

        # Gán sự kiện cho các ô nhập
        txt_tin_chi.textChanged.connect(lambda: self._on_tc_changed(row))
        txt_score.textChanged.connect(lambda: self._on_score_text_changed(row))

        # Kích hoạt tính toán ban đầu
        self._on_score_text_changed(row)

    def _on_score_text_changed(self, row: int):
        """Khi sinh viên nhập điểm, tự động cập nhật Grade và GPA tức thời"""
        if row >= self.tbl_mon_hoc.rowCount():
            return
        
        txt_score = self.tbl_mon_hoc.cellWidget(row, 2)
        lbl_grade = self.tbl_mon_hoc.cellWidget(row, 3)
        
        if not (txt_score and lbl_grade):
            return
            
        text = txt_score.text().strip().replace(",", ".")
        if not text:
            # Chưa nhập điểm
            lbl_grade.setText("--")
            lbl_grade.setProperty("diem_he_4", None)
            lbl_grade.setStyleSheet("""
                background-color: #F8F8EB;
                border: 1px solid #E5E7D8;
                border-radius: 7px;
                padding: 4px 8px;
                font-size: 13px;
                font-weight: 600;
                color: #9CA3AF;
            """)
        else:
            try:
                diem_so = float(text)
                grade_chu, diem_qd, _ = self.quy_doi_diem(diem_so)
                lbl_grade.setText(grade_chu)
                lbl_grade.setProperty("diem_he_4", diem_qd)
                
                # Màu sắc badge chữ cái điểm
                if "A" in grade_chu:
                    badge_bg = "#F0FDF4"
                    badge_border = "#ADBF15"
                    badge_color = "#365314"
                elif "B" in grade_chu:
                    badge_bg = "#EFF6FF"
                    badge_border = "#93C5FD"
                    badge_color = "#1E40AF"
                elif "C" in grade_chu:
                    badge_bg = "#FFFBEB"
                    badge_border = "#FCD34D"
                    badge_color = "#92400E"
                elif "D" in grade_chu:
                    badge_bg = "#FFF7ED"
                    badge_border = "#FDBA74"
                    badge_color = "#9A3412"
                else:
                    badge_bg = "#FEF2F2"
                    badge_border = "#FCA5A5"
                    badge_color = "#991B1B"
                    
                lbl_grade.setStyleSheet(f"""
                    background-color: {badge_bg};
                    border: 1.5px solid {badge_border};
                    border-radius: 7px;
                    padding: 4px 8px;
                    font-size: 13px;
                    font-weight: 800;
                    color: {badge_color};
                """)
            except ValueError:
                lbl_grade.setText("Lỗi")
                lbl_grade.setProperty("diem_he_4", None)
                lbl_grade.setStyleSheet("color: #EF4444; font-size: 12px; font-weight: 700;")
                
        self.tinh_gpa_hien_tai()

    def _on_tc_changed(self, row: int):
        """Khi số tín chỉ thay đổi thì tính lại GPA"""
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

    def xoa_dong_duoc_chon(self):
        """Xóa các dòng đang được chọn trong bảng"""
        selected = self.tbl_mon_hoc.selectedIndexes()
        if not selected:
            if self.tbl_mon_hoc.rowCount() > 0:
                self.xoa_mon(self.tbl_mon_hoc.rowCount() - 1)
            return
        rows = sorted(set(idx.row() for idx in selected), reverse=True)
        for r in rows:
            self.xoa_mon(r)

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
            try:
                tin_chi = float(txt_tc.text().strip()) if txt_tc else 0.0
            except ValueError:
                tin_chi = 0.0

            diem_qd = None
            if txt_sc and txt_sc.text().strip() and lbl_grade:
                diem_qd = lbl_grade.property("diem_he_4")

            ds_mon.append({
                "ten": ten,
                "tin_chi": tin_chi,
                "diem": diem_qd
            })
        return ds_mon

    def tinh_gpa_hien_tai(self):
        """Tính toán tổng tín chỉ, tổng điểm và GPA hiện tại tự động"""
        ds_mon = self.lay_du_lieu_mon()
        tong_tc_co_diem = 0.0
        tong_tc_toan_bo = 0.0
        tong_diem_tich_luy = 0.0

        for mon in ds_mon:
            tc = mon["tin_chi"]
            tong_tc_toan_bo += tc
            if mon["diem"] is not None and tc > 0:
                tong_tc_co_diem += tc
                tong_diem_tich_luy += mon["diem"] * tc

        if tong_tc_co_diem > 0:
            gpa = tong_diem_tich_luy / tong_tc_co_diem
        else:
            gpa = 0.0

        # Cập nhật nhãn kết quả trên thẻ bên phải
        self.lbl_tong_tin_chi.setText(f"{int(tong_tc_toan_bo) if tong_tc_toan_bo.is_integer() else tong_tc_toan_bo:.1f}")
        self.lbl_tong_diem.setText(f"{tong_diem_tich_luy:.2f}")
        self.lbl_gpa_hien_tai.setText(f"{gpa:.2f}")

        # Đánh giá xếp loại theo Quy chế đại học (UEL)
        if gpa >= 3.6:
            self.lbl_trang_thai_gpa.setText("Xếp loại: Xuất sắc (A+)")
            self.lbl_dong_vien.setText("Phong độ cực đỉnh, tiếp tục phát huy nhé!")
            self.lbl_gpa_hien_tai.setStyleSheet("color: #ADBF15; font-size: 64px; font-weight: 800;")
        elif gpa >= 3.2:
            self.lbl_trang_thai_gpa.setText("Xếp loại: Giỏi (A)")
            self.lbl_dong_vien.setText("Kết quả rất tốt, hãy tiếp tục duy trì nhé!")
            self.lbl_gpa_hien_tai.setStyleSheet("color: #556B2F; font-size: 64px; font-weight: 800;")
        elif gpa >= 2.5:
            self.lbl_trang_thai_gpa.setText("Xếp loại: Khá (B+)")
            self.lbl_dong_vien.setText("Cố gắng thêm chút nữa để chạm mốc Giỏi nhé!")
            self.lbl_gpa_hien_tai.setStyleSheet("color: #F4A46D; font-size: 64px; font-weight: 800;")
        elif gpa >= 2.0:
            self.lbl_trang_thai_gpa.setText("Xếp loại: Trung bình (C)")
            self.lbl_dong_vien.setText("Cần tập trung học tập để cải thiện thứ hạng!")
            self.lbl_gpa_hien_tai.setStyleSheet("color: #D97706; font-size: 64px; font-weight: 800;")
        else:
            self.lbl_trang_thai_gpa.setText("Xếp loại: Yếu / Kém (D/F)")
            self.lbl_dong_vien.setText("Cần chú ý lập kế hoạch học tập nghiêm túc!")
            self.lbl_gpa_hien_tai.setStyleSheet("color: #DC2626; font-size: 64px; font-weight: 800;")

        self.tinh_diem_can_dat()
        return gpa

    def tinh_diem_can_dat(self):
        """Tính điểm cần đạt cho các môn chưa có điểm để đạt GPA mục tiêu"""
        text_muc_tieu = self.txt_gpa_muc_tieu.text().strip().replace(",", ".")
        if not text_muc_tieu:
            self.lbl_diem_can_dat.setText("Điểm cần đạt các môn còn lại: --")
            self.lbl_diem_can_dat.setStyleSheet("color: #6B7280; font-size: 12px; font-weight: 600;")
            return

        try:
            gpa_muc_tieu = float(text_muc_tieu)
        except ValueError:
            self.lbl_diem_can_dat.setText("⚠️ GPA mục tiêu phải là số!")
            self.lbl_diem_can_dat.setStyleSheet("color: #EF4444; font-size: 12px; font-weight: 600;")
            return

        ds_mon = self.lay_du_lieu_mon()
        tc_da_co_diem = 0.0
        tong_diem_hien_tai = 0.0
        tc_chua_co_diem = 0.0

        for m in ds_mon:
            if m["diem"] is not None:
                tc_da_co_diem += m["tin_chi"]
                tong_diem_hien_tai += m["diem"] * m["tin_chi"]
            else:
                tc_chua_co_diem += m["tin_chi"]

        tong_tc = tc_da_co_diem + tc_chua_co_diem
        if tc_chua_co_diem == 0:
            if tong_tc > 0 and (tong_diem_hien_tai / tong_tc) >= gpa_muc_tieu:
                self.lbl_diem_can_dat.setText("🎉 Bạn đã đạt/vượt mức GPA mục tiêu!")
                self.lbl_diem_can_dat.setStyleSheet("color: #ADBF15; font-size: 12px; font-weight: 700;")
            else:
                self.lbl_diem_can_dat.setText("ℹ️ Tất cả môn đã có điểm.")
                self.lbl_diem_can_dat.setStyleSheet("color: #6B7280; font-size: 12px; font-weight: 600;")
            return

        # Điểm cần đạt = (GPA_muc_tieu * Tong_TC - Tong_diem_hien_tai) / TC_chua_co_diem
        diem_can_dat = (gpa_muc_tieu * tong_tc - tong_diem_hien_tai) / tc_chua_co_diem

        if diem_can_dat > 4.0:
            self.lbl_diem_can_dat.setText(f"❌ Không khả thi (cần {diem_can_dat:.2f} > 4.00)")
            self.lbl_diem_can_dat.setStyleSheet("color: #EF4444; font-size: 12px; font-weight: 700;")
        elif diem_can_dat <= 0:
            self.lbl_diem_can_dat.setText("🎉 Đã chắc chắn đạt mục tiêu!")
            self.lbl_diem_can_dat.setStyleSheet("color: #ADBF15; font-size: 12px; font-weight: 700;")
        else:
            self.lbl_diem_can_dat.setText(f"⚡ Cần đạt trung bình {diem_can_dat:.2f}/4.00 mỗi môn còn lại")
            self.lbl_diem_can_dat.setStyleSheet("color: #F4A46D; font-size: 12px; font-weight: 700;")

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
