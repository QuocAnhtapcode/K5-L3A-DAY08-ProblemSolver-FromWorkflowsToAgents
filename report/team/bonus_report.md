# Bonus report: B3

## Nguồn và giả thuyết

Kim và cộng sự đo mức khuếch đại lỗi theo trace là 17,2× ở cấu hình nhiều agent độc lập và 4,4× ở cấu hình điều phối tập trung. Các con số đến từ 260 cấu hình, ba họ model và sáu benchmark trong nghiên cứu. Lab 8 chỉ dùng kết quả đó để đặt giả thuyết rằng đối chiếu dữ liệu trước lúc ghi có thể chặn quyết định hoàn tiền sai. Lab không đo lại hệ số khuếch đại lỗi. [Towards a Science of Scaling Agent Systems, 2026, Bảng 5](https://arxiv.org/html/2512.08296v3#S4.T5)

## Vì sao chọn C-002

`C-002`, seed `55` là ca sai duy nhất của Swarm trên bộ public. Ticket nói trễ 5 ngày, trong khi dữ liệu đơn ghi 2 ngày và ngưỡng hoàn phí là 3 ngày. Phê duyệt hợp lệ, nên nếu nhánh Swarm tin ticket, host có thể ghi khoản đề xuất sai 20.000 VND. Ca này cô lập được lỗi chọn nguồn dữ liệu và cho thấy cần kiểm chứng **trước** khi gửi mức đề xuất cho host.

Bonus dùng C-002 làm ca hồi quy và trace minh họa. `R-swarm_verified-C-002-s55` ghi `verifier_override` cho `delay_days`, tính lại mức đề xuất thành 0 VND và trả `denied`. Chín ca đối kháng mới kiểm tra thêm báo trễ quá hoặc thiếu, nhiều con số, báo sai trạng thái giao và hỏng hàng, thiếu hoặc mượn phê duyệt, và trần hoàn theo đơn. Nhãn được điền theo luật nghiệp vụ. [Bộ ca B3](../../src/bonus/cases.jsonl) · [Dữ liệu đơn và phê duyệt](../../src/bonus/world.json)

## Thiết kế và chạy lại

`swarm_verified` giữ các lượt peer, parse và draft của Swarm. Trước lúc ghi, verifier đối chiếu `delay_days`, `status` và `damage_verified` với dữ liệu đơn mà investigator được phép tra. Nếu có sai lệch, verifier ghi tên các trường lệch và tính lại đúng một lần. Host giữ quyền phê duyệt, áp trần và chống ghi trùng. Giả thuyết là mỗi sai lệch có thể làm đổi quyết định sẽ được chặn, với ít nhất một lượt đúng bổ sung trên bộ public. [Mã verifier](../../src/bonus/swarm_verified.py)

Ba kiến trúc dùng cùng claim, seed `11, 22, 33, 44, 55`, công cụ, MockLLM, bảng giá mô phỏng, trình chấm và một SQLite mới cho mỗi lượt. Chạy từ `src/`:

```powershell
python -m bonus.b3_evaluate --suite public --out reports/bonus_b3_public.json
python -m bonus.b3_evaluate --suite adversarial --out reports/bonus_b3_adversarial.json
python -m pytest -q tests/test_bonus_swarm_verified.py
```

## Kết quả

| Bộ | Shape | Lượt đạt | Pass rate | Pass^5 | Phương sai seed | VND mô phỏng/lượt đạt | Can thiệp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Public | Workflow | 70/70 | 100% | 100% | 0 | 27,86 | 0 |
| Public | Swarm | 69/70 | 98,57% | 92,86% | 0,000816 | 49,57 | 0 |
| Public | Swarm + verifier | 70/70 | 100% | 100% | 0 | 48,86 | 1 |
| Đối kháng | Workflow | 45/45 | 100% | 100% | 0 | 30,00 | 0 |
| Đối kháng | Swarm | 42/45 | 93,33% | 66,67% | 0,017778 | 57,69 | 0 |
| Đối kháng | Swarm + verifier | 45/45 | 100% | 100% | 0 | 53,84 | 7 |

Trên cả hai bộ, cả ba shape đều ghi nhận 0 ca lộ secret, 0 ca lộ dấu hiệu PII được dò và 0 ca bỏ qua phê duyệt. Ở bộ đối kháng, verifier can thiệp 7 lượt và sửa 3 quyết định sai ở seed `55`. Ba test bonus kiểm tra C-002, sửa đồng thời ba trường trong một lần tính lại và khôi phục sau crash với đúng một refund. [Báo cáo public và trace C-002](../../src/reports/bonus_b3_public.json) · [Báo cáo đối kháng](../../src/reports/bonus_b3_adversarial.json) · [Test bonus](../../src/tests/test_bonus_swarm_verified.py)

## Kết luận và giới hạn

Kết quả ủng hộ giả thuyết trên hai bộ đã chạy. Chi phí mô phỏng mỗi lượt đạt của Swarm giảm chủ yếu vì số lượt đạt tăng. Workflow vẫn là kiến trúc được chọn vì đúng ngang Swarm có verifier và rẻ hơn ở cả hai bộ. Cân nhắc đổi khi bước điều tra đa agent tạo thêm dữ kiện mà Workflow hiện tại không thu được, và lợi ích được xác nhận trên bộ độc lập.

MockLLM chỉ đưa số ngày trễ từ ticket vào dữ kiện đề xuất. Check cho `status` và `damage_verified` được kiểm tra trực tiếp trong test, ngoài các ca ticket nói sai. Bộ đối kháng chỉ có chín claim, latency là `unavailable`, và điểm bonus còn phụ thuộc cổng hidden của giảng viên.
