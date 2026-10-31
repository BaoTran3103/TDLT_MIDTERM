import os
import sys
import importlib
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTableWidgetItem, QLineEdit, 
    QComboBox, QPushButton, QLabel, QHBoxLayout, QMessageBox, QHeaderView
)

# Load module UI cùng thư mục (xử lý tiền tố số 01_ theo convention)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

ui_module = importlib.import_module("01_MainScreen")
Ui_MainScreen = ui_module.Ui_MainScreen


# Thang điểm quy đổi chuẩn theo hình tham khảo
THANG_DIEM = {
    "A+": 4.00,
    "A": 4.00,
    "A-": 3.67,
    "B+": 3.33,
    "B": 3.00,
    "B-": 2.67,
    "C+": 2.33,
    "C": 2.00,
    "D": 1.00,
    "F": 0.00
}


class MainScreen_Ext(QMainWindow, Ui_MainScreen):
    """
    Class xử lý logic cho màn hình chính GPA Calculator
    Tuân thủ quy chuẩn CONVENTION.md
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._cai_dat_bang()
        self._ket_noi_su_kien()
        self._khoi_tao_du_lieu_mau()
        self.tinh_gpa_hien_tai()

    def _cai_dat_bang(self):
        """Cấu hình bảng tbl_mon_hoc theo tỉ lệ và giao diện tham khảo"""
        header = self.tbl_mon_hoc.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)         # Course
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)           # Credit Hours
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)           # Grade
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)           # Grade Points
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)           # Action
        
        self.tbl_mon_hoc.setColumnWidth(1, 140)
        self.tbl_mon_hoc.setColumnWidth(2, 130)
        self.tbl_mon_hoc.setColumnWidth(3, 140)
        self.tbl_mon_hoc.setColumnWidth(4, 90)
        
        self.tbl_mon_hoc.verticalHeader().setVisible(False)
        self.tbl_mon_hoc.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl_mon_hoc.setShowGrid(False)

    def _ket_noi_su_kien(self):
        """Kết nối các nút với hàm xử lý tương ứng"""
        self.btn_them_mon.clicked.connect(lambda: self.them_mon())
        self.btn_xoa_mon.clicked.connect(self.xoa_dong_duoc_chon)
        self.btn_tinh_gpa.clicked.connect(self.xu_ly_tinh_gpa)
        self.txt_gpa_muc_tieu.textChanged.connect(self.tinh_diem_can_dat)

    def _khoi_tao_du_lieu_mau(self):
        """Nạp dữ liệu mẫu ban đầu giống y hệt hình mẫu"""
        ds_mau = [
            ("Calculus I", 4, "A"),
            ("Physics I", 4, "B+"),
            ("English Composition", 3, "A-"),
            ("Computer Science I", 3, "B"),
            ("History 101", 3, "A"),
        ]
        for ten, tin_chi, diem in ds_mau:
            self.them_mon(ten, tin_chi, diem)

    def them_mon(self, ten: str = "", tin_chi: int = 3, diem: str = "A"):
        """
        Thêm một dòng môn học vào bảng với các widget ô nhập, combobox điểm và nút xóa
        """
        row = self.tbl_mon_hoc.rowCount()
        self.tbl_mon_hoc.insertRow(row)
        self.tbl_mon_hoc.setRowHeight(row, 56)

        # 1. Cột Tên môn (QLineEdit)
        txt_ten = QLineEdit(ten)
        txt_ten.setPlaceholderText("Nhập tên môn học...")
        txt_ten.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #E5E7EB;
                border-radius: 8px;
                padding: 6px 12px;
                background-color: #FFFFFF;
                font-size: 13px;
                color: #111827;
            }
            QLineEdit:focus {
                border: 1.5px solid #ADBF15;
            }
        """)
        self.tbl_mon_hoc.setCellWidget(row, 0, txt_ten)

        # 2. Cột Số tín chỉ (QLineEdit)
        txt_tin_chi = QLineEdit(str(tin_chi))
        txt_tin_chi.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        txt_tin_chi.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #E5E7EB;
                border-radius: 8px;
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
        txt_tin_chi.textChanged.connect(lambda: self._on_row_value_changed(row))
        self.tbl_mon_hoc.setCellWidget(row, 1, txt_tin_chi)

        # 3. Cột Điểm chữ (QComboBox)
        cbo_diem = QComboBox()
        for d in THANG_DIEM.keys():
            cbo_diem.addItem(d)
        cbo_diem.addItem("Chưa có điểm")
        
        idx = cbo_diem.findText(diem)
        if idx >= 0:
            cbo_diem.setCurrentIndex(idx)
        else:
            cbo_diem.setCurrentText("A")
            
        cbo_diem.setStyleSheet("""
            QComboBox {
                border: 1.5px solid #E5E7EB;
                border-radius: 8px;
                padding: 6px 10px;
                background-color: #FFFFFF;
                font-size: 13px;
                font-weight: 600;
                color: #111827;
            }
            QComboBox:focus {
                border: 1.5px solid #ADBF15;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left-width: 0px;
            }
        """)
        cbo_diem.currentIndexChanged.connect(lambda: self._on_row_value_changed(row))
        self.tbl_mon_hoc.setCellWidget(row, 2, cbo_diem)

        # 4. Cột Điểm quy đổi (QLabel)
        diem_qd = THANG_DIEM.get(diem, 0.0)
        lbl_diem = QLabel(f"{diem_qd:.2f}" if diem in THANG_DIEM else "--")
        lbl_diem.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        lbl_diem.setStyleSheet("""
            color: #556B2F;
            font-size: 14px;
            font-weight: 700;
        """)
        self.tbl_mon_hoc.setCellWidget(row, 3, lbl_diem)

        # 5. Cột Nút Xóa (QPushButton dạng thùng rác 🗑)
        btn_xoa = QPushButton("🗑")
        btn_xoa.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn_xoa.setToolTip("Xóa môn này")
        btn_xoa.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 16px;
                color: #9CA3AF;
                padding: 4px;
            }
            QPushButton:hover {
                color: #EF4444;
                font-size: 18px;
            }
        """)
        btn_xoa.clicked.connect(lambda: self._xoa_mon_tai_widget(btn_xoa))
        self.tbl_mon_hoc.setCellWidget(row, 4, btn_xoa)

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
            # Rebind lại tín chỉ và điểm quy đổi sau khi dòng bị xóa
            self._cap_nhat_lai_cac_dong()
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

    def _on_row_value_changed(self, row: int):
        """Cập nhật điểm quy đổi và tính lại GPA khi người dùng thay đổi giá trị"""
        if row >= self.tbl_mon_hoc.rowCount():
            return
        cbo_diem = self.tbl_mon_hoc.cellWidget(row, 2)
        lbl_diem = self.tbl_mon_hoc.cellWidget(row, 3)
        if isinstance(cbo_diem, QComboBox) and isinstance(lbl_diem, QLabel):
            text_diem = cbo_diem.currentText()
            if text_diem in THANG_DIEM:
                diem_so = THANG_DIEM[text_diem]
                lbl_diem.setText(f"{diem_so:.2f}")
                lbl_diem.setStyleSheet("color: #556B2F; font-size: 14px; font-weight: 700;")
            else:
                lbl_diem.setText("--")
                lbl_diem.setStyleSheet("color: #9CA3AF; font-size: 14px; font-weight: 600;")
        self.tinh_gpa_hien_tai()

    def _cap_nhat_lai_cac_dong(self):
        """Cập nhật lại kết nối sự kiện các dòng sau khi xóa"""
        for r in range(self.tbl_mon_hoc.rowCount()):
            txt_tc = self.tbl_mon_hoc.cellWidget(r, 1)
            cbo = self.tbl_mon_hoc.cellWidget(r, 2)
            if txt_tc and cbo:
                try:
                    txt_tc.textChanged.disconnect()
                except Exception:
                    pass
                try:
                    cbo.currentIndexChanged.disconnect()
                except Exception:
                    pass
                current_r = r
                txt_tc.textChanged.connect(lambda _, row=current_r: self._on_row_value_changed(row))
                cbo.currentIndexChanged.connect(lambda _, row=current_r: self._on_row_value_changed(row))

    def lay_du_lieu_mon(self):
        """
        Đọc và trả về danh sách các môn học dưới dạng dict theo quy chuẩn CONVENTION.md:
        [{"ten": "Toan", "tin_chi": 3, "diem": 4.0}, ...]
        """
        ds_mon = []
        for r in range(self.tbl_mon_hoc.rowCount()):
            txt_ten = self.tbl_mon_hoc.cellWidget(r, 0)
            txt_tc = self.tbl_mon_hoc.cellWidget(r, 1)
            cbo_diem = self.tbl_mon_hoc.cellWidget(r, 2)

            ten = txt_ten.text().strip() if txt_ten else ""
            try:
                tin_chi = float(txt_tc.text().strip()) if txt_tc else 0.0
            except ValueError:
                tin_chi = 0.0

            diem_chu = cbo_diem.currentText() if cbo_diem else ""
            diem_so = THANG_DIEM.get(diem_chu, None)

            ds_mon.append({
                "ten": ten,
                "tin_chi": tin_chi,
                "diem": diem_so
            })
        return ds_mon

    def tinh_gpa_hien_tai(self):
        """Tính toán tổng tín chỉ, tổng điểm và GPA hiện tại"""
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

        # Thông điệp động viên theo mức điểm và màu sắc nhận diện
        if gpa >= 3.6:
            self.lbl_trang_thai_gpa.setText("Xuất Sắc! (Excellent)")
            self.lbl_dong_vien.setText("Phong độ cực đỉnh, tiếp tục phát huy nhé!")
            self.lbl_gpa_hien_tai.setStyleSheet("color: #ADBF15; font-size: 64px; font-weight: 800;")
        elif gpa >= 3.2:
            self.lbl_trang_thai_gpa.setText("Good Job!")
            self.lbl_dong_vien.setText("Keep up the great work.")
            self.lbl_gpa_hien_tai.setStyleSheet("color: #556B2F; font-size: 64px; font-weight: 800;")
        elif gpa >= 2.5:
            self.lbl_trang_thai_gpa.setText("Khá Tốt (Pretty Good)")
            self.lbl_dong_vien.setText("Cố gắng thêm chút nữa để chạm mốc A nhé!")
            self.lbl_gpa_hien_tai.setStyleSheet("color: #F4A46D; font-size: 64px; font-weight: 800;")
        else:
            self.lbl_trang_thai_gpa.setText("Cần Cố Gắng (Keep Pushing)")
            self.lbl_dong_vien.setText("Hãy lên kế hoạch học tập để cải thiện điểm số!")
            self.lbl_gpa_hien_tai.setStyleSheet("color: #DC2626; font-size: 64px; font-weight: 800;")

        self.tinh_diem_can_dat()
        return gpa

    def tinh_diem_can_dat(self):
        """Tính điểm cần đạt cho các môn chưa có điểm để đạt GPA mục tiêu"""
        text_muc_tieu = self.txt_gpa_muc_tieu.text().strip()
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

    def xu_ly_tinh_gpa(self):
        """Hàm xử lý khi click nút CALCULATE GPA"""
        gpa = self.tinh_gpa_hien_tai()
        self.statusBar().showMessage(f"Đã cập nhật GPA thành công: {gpa:.2f}", 3000)
