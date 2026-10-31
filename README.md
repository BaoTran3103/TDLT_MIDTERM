# TDLT_MIDTERM - Công cụ tính GPA

Ứng dụng desktop viết bằng Python và PyQt6 (giao diện thiết kế bằng Qt Designer). Người dùng nhập danh sách môn học, ứng dụng tính GPA hiện tại và điểm cần đạt ở các môn còn lại để đạt GPA mục tiêu.

## Tính năng

**Hai màn hình**
- Màn hình nhập môn học: chỉ hiện danh sách môn học và nút **Tính GPA**.
- Màn hình kết quả: hiện sau khi bấm **Tính GPA** và dữ liệu hợp lệ, gồm GPA, xếp loại, thang điểm quy đổi và GPA mục tiêu. Nút **Quay lại** ở góc phải trên để về màn hình nhập.

**Bảng môn học**
- Cột số thứ tự tự đánh lại khi thêm hoặc xóa dòng.
- Thêm môn bằng **Thêm môn học**, xóa từng dòng bằng biểu tượng thùng rác.
- Chọn nhiều dòng để xóa, giống Excel:
  - Click: chọn một dòng.
  - Shift + click: chọn một dãy dòng.
  - Ctrl (⌘ trên Mac) + click: thêm hoặc bỏ từng dòng.
- Điểm chữ tự cập nhật theo điểm nhập.

**Thang điểm Hệ 10 và Hệ 4**
- Chuyển thang bằng hai nút trên bảng, điểm đã nhập tự quy đổi.
- Tiêu đề cột và ô nhập hiển thị mức tối đa (0 - 10 hoặc 0 - 4).
- GPA, tổng điểm tích lũy, thang điểm tối đa và công thức đều đổi theo thang đang chọn.

**Kiểm tra dữ liệu**
- Tên môn không để trống.
- Số tín chỉ lớn hơn 0 và tối đa 10.
- Điểm nằm trong thang đang chọn, hoặc để trống nếu môn chưa có điểm.
- Ô sai được viền đỏ, hộp thoại báo lỗi nêu rõ dòng nào sai.

**GPA mục tiêu**
- Nhập mục tiêu theo thang đang chọn.
- Hiển thị điểm trung bình tối thiểu cần đạt và liệt kê từng môn chưa có điểm.
- Báo "Không khả thi" hoặc "Đã đạt mục tiêu" khi phù hợp.

## Công thức

```
GPA = ∑ (Điểm × Số tín chỉ) / ∑ Số tín chỉ
```

Chỉ tính các môn đã có điểm. Điểm chỉ làm tròn khi hiển thị (2 chữ số thập phân).

Bảng quy đổi theo quy chế đào tạo:

| Điểm chữ | Thang 10 | Thang 4 | Xếp loại |
|---|---|---|---|
| A+ | 9.0 - 10.0 | 4.0 | Xuất sắc |
| A | 8.0 - 8.9 | 3.5 | Giỏi |
| B+ | 7.0 - 7.9 | 3.0 | Khá |
| B | 6.0 - 6.9 | 2.5 | Trung bình khá |
| C | 5.0 - 5.9 | 2.0 | Trung bình |
| D+ | 4.0 - 4.9 | 1.5 | Yếu |
| D | 3.0 - 3.9 | 1.0 | Kém |
| F | dưới 3.0 | 0.0 | Kém |

## Ảnh chụp màn hình

| Màn hình nhập môn học | Màn hình kết quả |
|---|---|
| _Thêm ảnh vào đây_ | _Thêm ảnh vào đây_ |

## Cấu trúc

```
TDLT_MIDTERM/
├── Client/
│   ├── ClientDataset/
│   └── ClientUI/
│       ├── 01_FirstScreen/
│       └── 01_MainScreen/
│           ├── 01_MainScreen.ui        # giao diện (Qt Designer)
│           ├── 01_MainScreen.py        # sinh từ .ui, không sửa tay
│           └── 01_MainScreen_Ext.py    # code xử lý
├── Images/
│   └── icons/                          # icon SVG dùng trong giao diện
├── MyApp.py                            # điểm khởi chạy
├── CONVENTION.md
└── README.md
```

Mỗi màn hình mới là một thư mục `<số>_<TênMànHình>/` gồm 3 file cùng tên: `.ui`, `.py` (sinh từ `.ui`) và `_Ext.py` (code xử lý). Chi tiết xem [CONVENTION.md](CONVENTION.md).

## Chạy chương trình

Yêu cầu: Python 3.10 trở lên.

```bash
git clone <link-repo>
cd TDLT_MIDTERM
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install PyQt6
python MyApp.py
```

## Quy ước dữ liệu

Dữ liệu một môn dùng chung toàn nhóm:

```python
{"ten": "Toan", "tin_chi": 3, "diem": 3.5}   # chưa có điểm: "diem": None
```

Trong `lay_du_lieu_mon()`, trường `diem` luôn là điểm quy đổi theo thang 4.

## Phân công

| Task | Việc cần làm | Hàm | Người làm |
|---|---|---|---|
| 1 | Bảng môn học, thêm/xóa môn | `them_mon()`, `xoa_mon()`, `xoa_dong_duoc_chon()` | |
| 2 | Khu vực GPA mục tiêu và kết quả | `tinh_diem_can_dat()` | |
| 3 | Đọc và kiểm tra dữ liệu | `lay_du_lieu_mon()`, `kiem_tra_du_lieu()` | |
| 4 | Tính GPA | `tinh_gpa_theo_diem()`, `tinh_gpa_hien_tai()` | |
| 5 | Luồng tính, kết nối nút | `xu_ly_tinh_gpa()` | |

## Việc còn lại

- [ ] Ba kịch bản điểm cho các môn chưa có điểm: chia đều, đạt 10 ở một môn nhiều tín chỉ nhất, đạt 10 ở hai môn nhiều tín chỉ nhất.
- [ ] Cố định bảng đúng 6 môn theo đề bài.
- [ ] Chuẩn bị `main.py` và `gpa_app.ui` để nộp.
- [ ] Bộ test các trường hợp theo kế hoạch.

## Làm việc nhóm

Quy trình Git (branch, commit, Pull Request) và quy ước đặt tên xem [CONVENTION.md](CONVENTION.md). Không push trực tiếp lên `main` và `dev`.
