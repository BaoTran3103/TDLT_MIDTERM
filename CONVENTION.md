# CONVENTION

## 1. Git: các bước làm một task

1. Lấy `dev` mới nhất:
   ```bash
   git checkout dev
   git pull origin dev
   ```
2. Tạo branch mới từ `dev`:
   ```bash
   git checkout -b feature/task1-bang-mon-hoc
   ```
3. Code, commit nhỏ (mỗi commit một việc).
4. Cập nhật `dev` vào branch, xử lý conflict nếu có:
   ```bash
   git fetch origin
   git rebase origin/dev
   ```
5. Chạy thử chương trình, xóa `print()` debug.
6. Push branch:
   ```bash
   git push origin feature/task1-bang-mon-hoc
   ```
7. Tạo Pull Request vào `dev`.
8. Chờ ít nhất 1 người approve, sửa theo comment.
9. Bấm **Squash and merge**, xóa branch.
10. Mọi người `git pull origin dev`.

Không push trực tiếp lên `main` và `dev`.

### Tên branch

`<loại>/<mô-tả-ngắn>`, viết thường, nối bằng `-`, không dấu.

| Loại | Dùng khi | Ví dụ |
|---|---|---|
| `feature/` | Chức năng mới | `feature/task2-gpa-muc-tieu` |
| `fix/` | Sửa lỗi | `fix/tinh-gpa-mon-chua-co-diem` |
| `docs/` | Sửa tài liệu | `docs/cap-nhat-readme` |
| `chore/` | Cấu hình, thư viện | `chore/them-gitignore` |

### Commit

Format: `<type>(<phạm vi>): <mô tả tiếng Việt>`

- `type`: `feat`, `fix`, `refactor`, `style`, `docs`, `test`, `chore`
- Mô tả ngắn dưới 72 ký tự, không chấm cuối câu.
- Cấm: `update`, `fix bug`, `abc`, `wip`.

```
feat(bang-mon): thêm hàm them_mon và xoa_mon
feat(ket-qua): thêm ô nhập GPA mục tiêu
fix(tinh-gpa): xử lý môn chưa có điểm
docs(readme): thêm bảng phân công
chore: thêm .gitignore
```

### Pull Request

- Tiêu đề giống commit: `feat(bang-mon): thêm hàm them_mon và xoa_mon`
- Mỗi PR một task.
- Nội dung PR:

```markdown
## Mô tả
## Task liên quan
## Cách test
## Checklist
- [ ] Đã tự review code
- [ ] Đã chạy thử, không báo lỗi
- [ ] Đặt tên đúng convention
- [ ] Không còn print() debug
```

- Không tự approve PR của mình.
- Reviewer phản hồi trong 24 giờ.

## 2. Code: các bước khi viết

1. **Tạo giao diện mới** trong `AdminUI/` hoặc `ClientUI/` theo đúng cấu trúc:
   ```
   ClientUI/
   └── 02_SecondScreen/
       ├── 02_SecondScreen.ui        # tạo bằng Qt Designer
       ├── 02_SecondScreen.py        # sinh từ .ui, không sửa tay
       └── 02_SecondScreen_Ext.py    # code xử lý, viết ở đây
   ```
   - Mỗi màn hình một thư mục riêng, tên `<số>_<TênMànHình>` (số 2 chữ số, tăng dần: `01_`, `02_`, ...).
   - Tên thư mục và 3 file bên trong **phải trùng nhau**.
   - Tên màn hình viết `PascalCase`, không dấu, không khoảng trắng.
   - `Admin` và `Client` có số thứ tự riêng, mỗi bên đếm từ `01_`.
2. **Không sửa tay** file `.py` sinh từ `.ui`. Mọi hàm xử lý viết trong file `_Ext.py`.
3. **Mỗi người chỉ sửa file `.ui` của task mình**, tránh conflict.
4. **Tên hàm, biến:** `snake_case`, tiếng Việt không dấu (`them_mon`, `ds_mon`, `gpa_muc_tieu`).
5. **Hằng số:** `UPPER_SNAKE_CASE` (`DIEM_TOI_DA = 10`).
6. **Tên widget trong Qt Designer:** `btn_` (nút), `tbl_` (bảng), `txt_` (ô nhập), `lbl_` (nhãn). Ví dụ `btn_tinh_gpa`, `tbl_mon_hoc`.
7. **Dữ liệu một môn** dùng chung toàn nhóm:
   ```python
   {"ten": "Toan", "tin_chi": 3, "diem": 8.5}   # chưa có điểm: "diem": None
   ```
8. **Hàm tính toán** (`tinh_gpa_hien_tai`, `tinh_diem_can_dat`) chỉ nhận dữ liệu và `return`, không đụng vào widget.
9. **`kiem_tra_du_lieu`** trả về `(hop_le, thong_bao)`.
10. **Báo lỗi** bằng `QMessageBox`, tiếng Việt có dấu, nói rõ sai ở đâu.
11. **Làm tròn** chỉ khi hiển thị: `f"{gpa:.2f}"`.
12. Indent 4 spaces, mỗi hàm một việc, xóa code thừa trước khi commit.
13. Comment và docstring viết tiếng Việt có dấu.