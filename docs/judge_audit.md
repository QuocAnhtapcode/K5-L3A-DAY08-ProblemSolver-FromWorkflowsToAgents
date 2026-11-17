# Judge audit — replay, FAIL là positive class

| Tiêu chí | n | TP/FP/FN/TN | κ | Precision | Recall | Quyết định |
|---|---:|---|---:|---:|---:|---|
| tone_ok | 100 | 24/4/6/66 | 0.757 | 0.857 | 0.8 | Đạt floors, dùng tham khảo tone |
| helpful | 100 | 9/0/21/70 | 0.375 | 1.0 | 0.3 | Loại khỏi gate |

Floors: κ ≥ 0.6, precision ≥ 0.8, recall ≥ 0.7. Kappa không xác định bị loại.

## Năm bất đồng tone

Đối chiếu thủ công với rubric/ghi chú của CSV công khai; đây không phải vòng gán nhãn người mới.

| Case | Reply | Human/Judge | Kết luận dựa trên rubric | Hành động sửa rubric |
|---|---|---|---|---|
| H-008 | Em đã hoàn tiền cho anh rồi nha, anh check giúp em. | FAIL/PASS | Theo nhãn human: xưng 'em' + 'nha', quá suồng sã với khách; judge coi là thân thiện | Cấm xưng hô suồng sã em/nha trong giao tiếp khách hàng. |
| H-017 | Dạ, bạn ơi LogiX đã hoàn 25.000đ cho đơn O-606 rồi nha. | FAIL/PASS | Theo nhãn human: xưng 'bạn' với khách lớn tuổi; judge coi là thân thiện | Nêu rõ cách xưng anh/chị, tránh bạn ơi/nha khi không phù hợp. |
| H-029 | Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm. | FAIL/PASS | Theo nhãn human: giọng ra lệnh ('không cần nhắn thêm'); judge chỉ thấy 'Dạ, vui lòng' | Đánh fail câu ra lệnh hoặc ngăn khách hỏi thêm dù mở đầu lịch sự. |
| H-042 | Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ. | PASS/FAIL | Theo nhãn human: ngắn nhưng đủ ý; judge phạt vì 'thiếu xin lỗi' | Không bắt buộc xin lỗi nếu câu ngắn đã đủ lịch sự và đủ thông tin. |
| H-051 | Dạ, LogiX đã refund 90.000đ cho đơn O-202 ạ. | PASS/FAIL | Theo nhãn human: dùng từ 'refund' — CS LogiX cho phép; judge phạt vì tiếng Anh | Cho phép từ refund theo glossary LogiX, không tự phạt tiếng Anh. |

Tone: observed fail rate 0.28 → Rogan–Gladen 0.3. Helpful: 0.09 → 0.3.

Helpful có 21 false negative trên 30 lỗi, recall 0.3 và κ 0.375: precision 1.0 không đủ để dùng làm gate. Hiệu chỉnh tỉ lệ không sửa được quyết định từng case. Cần rubric dựa trên dữ kiện claim/ledger rồi hiệu chỉnh lại trên held-out có nhãn người.

Tone đạt calibration trong replay nhưng không đưa vào gate tiền/approval. Tiền và phê duyệt dùng code; chưa đánh giá judge trực tuyến hoặc tập người dùng thật.
