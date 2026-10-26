# TDLT_MIDTERM - Tính GPA

Ứng dụng Python + PyQt (Qt Designer): nhập môn học, tính GPA hiện tại và điểm cần đạt để đạt GPA mục tiêu.

## Cấu trúc

```
TDLT_MIDTERM/
├── Admin/
│   ├── AdminDataset/data.json
│   └── AdminUI/01_FirstScreen/
├── Client/
│   ├── ClientDataset/data.json
│   └── ClientUI/01_FirstScreen/
├── Images/
├── MyApp.py
├── CONVENTION.md
└── README.md
```

Mỗi màn hình mới trong `AdminUI/` hoặc `ClientUI/` là một thư mục `<số>_<TênMànHình>/` gồm 3 file cùng tên:
- `.ui`: giao diện (Qt Designer)
- `.py`: sinh từ `.ui`, không sửa tay
- `_Ext.py`: code xử lý

Chi tiết xem [CONVENTION.md](CONVENTION.md).

## Chạy chương trình

1. `git clone <link-repo>` rồi `cd TDLT_MIDTERM`
2. `python3 -m venv .venv`
3. `source .venv/bin/activate` (Windows: `.venv\Scripts\activate`)
4. `pip install PyQt6`
5. `python MyApp.py`

## Phân công

| Task | Việc cần làm | Hàm | Người làm |
|---|---|---|---|
| 1 | Bảng môn học, thêm/xóa môn | `them_mon()`, `xoa_mon()` | |
| 2 | Khu vực GPA mục tiêu và kết quả | `lay_gpa_muc_tieu()`, `hien_thi_ket_qua()` | |
| 3 | Đọc và kiểm tra dữ liệu | `lay_du_lieu_mon()`, `kiem_tra_du_lieu()` | |
| 4 | Tính GPA | `tinh_gpa_hien_tai()`, `tinh_diem_can_dat()` | |
| 5 | Luồng tính, kết nối nút | `xu_ly_tinh_gpa()` | |

## Làm việc nhóm

Xem [CONVENTION.md](CONVENTION.md).