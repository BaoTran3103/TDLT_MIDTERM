# thuvien.py: File chứa các hàm thuật toán tính toán GPA dự báo và đưa ra lời khuyên


def tinh_toan_ket_qua_gpa(danh_sach_mon):
  """Hàm tính điểm GPA trung bình tích lũy có trọng số từ các môn đã biết.

  - danh_sach_mon: Danh sách gồm các tuple hoặc list: (so_tin_chi, diem_so)
  """
  tong_diem_nhan_tc = 0.0
  tong_tin_chi = 0

  for tin_chi, diem in danh_sach_mon:
    # Chỉ tính toán khi người dùng nhập đầy đủ số hợp lệ lớn hơn 0
    if tin_chi > 0 and diem >= 0:
      tong_diem_nhan_tc += diem * tin_chi
      tong_tin_chi += tin_chi

  # Tránh lỗi chia cho 0
  if tong_tin_chi == 0:
    return 0.0

  gpa_du_kien = tong_diem_nhan_tc / tong_tin_chi
  return round(gpa_du_kien, 2)


def danh_gia_trang_thai_va_loi_khuyen(projected_gpa):
  """Đưa ra trạng thái học lực và lời khuyên thông minh dựa trên GPA dự báo"""
  if projected_gpa >= 3.6:
    status = "Xuất sắc 🌟"
    advice = (
        "💡 Quá đỉnh! Mức điểm này giúp bạn dễ dàng đạt học bổng loại Xuất"
        " sắc. Hãy duy trì phong độ này nhé!"
    )
  elif projected_gpa >= 3.2:
    status = "Giỏi 🎯"
    advice = (
        "💡 Rất tốt! Bạn đang ở top sinh viên giỏi. Cố gắng thêm chút ở các môn"
        " chuyên ngành là chạm mốc A+."
    )
  elif projected_gpa >= 2.5:
    status = "Khá 👍"
    advice = (
        "💡 Ổn định! Tuy nhiên cần chú ý cải thiện điểm số các môn có số tín"
        " chỉ lớn để kéo GPA lên cao hơn."
    )
  elif projected_gpa > 0:
    status = "Trung bình ⚠️"
    advice = (
        "💡 Cần cố gắng nhiều hơn! Hãy lập kế hoạch ôn tập kỹ càng cho các bài"
        " kiểm tra giữa kỳ và cuối kỳ."
    )
  else:
    status = "Chưa rõ"
    advice = (
        "💡 Vui lòng nhập đầy đủ số tín chỉ và điểm số của các môn học bên"
        " trái!"
    )

  return status, advice