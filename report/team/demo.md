# Demo Lab 8 — LogiX-VN | ProblemSolver

Kịch bản khoảng 8 phút cho buổi trình bày hoặc quay màn hình. Nội dung bám CP1–CP5, ba điều kiện must-pass và bonus B3. Điều chỉnh thời lượng theo hướng dẫn của coach nếu có. [Checkpoints](../../CHECKPOINTS.md) · [Rubric](../../RUBRIC.md)

## Chuẩn bị trước khi trình bày

Mở PowerShell ở thư mục gốc repo, đặt cửa sổ terminal cạnh file này. Nếu `.venv` đã có thư viện của lab, dùng các lệnh sau. Nếu chưa có, chạy `python -m venv .venv` trong `src/`, sau đó chạy `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`.

```powershell
cd src
$lab8Python = '.\.venv\Scripts\python.exe'
& $lab8Python -m lab8.smoke
& $lab8Python -m scripts.demo_lab8
```

`lab8.smoke pass` xác nhận môi trường sẵn sàng. Demo mặc định chạy các ca nghiệp vụ, crash suite và ca bonus trực tiếp, rồi đọc bảng benchmark đã lưu. SQLite và trace của demo nằm trong thư mục tạm, nên chạy lại từ đầu vẫn có dữ liệu sạch. Khi trình bày, dùng `--section` để dừng sau từng nội dung. [Mã chạy demo](../../src/scripts/demo_lab8.py)

| Thời lượng | Phần | Lệnh từ `src/` |
| --- | --- | --- |
| 0:00–0:40 | Bài toán và phạm vi | Mở repo và nói phần mở đầu |
| 0:40–1:45 | Bốn kiến trúc chạy cùng C-001 | `& $lab8Python -m scripts.demo_lab8 --section shapes` |
| 1:45–2:30 | Handoff và quyền đọc | `& $lab8Python -m scripts.demo_lab8 --section handoff` |
| 2:30–3:35 | Phê duyệt và trần hoàn theo đơn | `& $lab8Python -m scripts.demo_lab8 --section policy` |
| 3:35–5:05 | Crash, retry và ledger | `& $lab8Python -m scripts.demo_lab8 --section crash` |
| 5:05–6:25 | Benchmark và quyết định ADR | `& $lab8Python -m scripts.demo_lab8 --section benchmark` |
| 6:25–8:00 | C-002, bonus B3 và kết luận | `& $lab8Python -m scripts.demo_lab8 --section bonus` |

## Lời thoại và điểm cần chỉ trên màn hình

### 0. Mở đầu

**Nói:** «Nhóm ProblemSolver mô phỏng xử lý yêu cầu hoàn phí của LogiX-VN. Chúng em chạy cùng dữ liệu trên bốn kiến trúc và chọn kiến trúc ít tự chủ nhất mà vẫn xử lý đúng. Agent hỗ trợ tra cứu. Code tính tiền từ dữ liệu đơn và chính sách, còn host kiểm phê duyệt, áp trần và ghi giao dịch.»

**Ý nghĩa:** Đặt tiêu chí trước khi mở kết quả. Demo sẽ đối chiếu quyết định với dữ liệu đơn, ledger và trace.

### 1. Chạy cùng claim qua bốn kiến trúc

**Mục đích:** Cố định `C-001`, seed `11` và dùng một SQLite mới cho mỗi kiến trúc để thấy khác biệt về cách làm.

**Chỉ trên màn hình:** Cả bốn trả `resolved`, đề xuất và ghi **35.000 VND**, mỗi lượt có một `refund_committed`. Single Agent in các công cụ đọc mà vòng ReAct chọn. Workflow có `model=0`.

**Nói:** «Workflow chạy các bước Python cố định. Single Agent chọn tool đọc trong vòng tối đa tám bước. Orchestrator giao việc đọc cho investigator. Swarm là bản tham chiếu có các lượt peer, parse và draft. Kết quả giống nhau ở ca này, nên cần benchmark cả bộ để so sánh.»

### 2. Handoff và trace

**Mục đích:** Dùng `C-010` để kiểm tra việc giao quyền cho investigator và khả năng kiểm chứng trace.

**Chỉ trên màn hình:** Handoff có `owner_order_only` và duy nhất `lookup_order`. Demo chỉ hiện tên các trường, công cụ được cấp và kết quả kiểm tra trace theo nhãn public. Mở `make_handoff` hoặc `orchestrator.py` khi được hỏi cách làm.

**Nói:** «Orchestrator dùng allowlist để tạo handoff. Investigator tra được dữ liệu trong phạm vi chủ đơn. Trace cần vừa đủ cho grader kiểm tra và bỏ ticket thô, header, secret, số điện thoại và địa chỉ.» [Hợp đồng trace](../../docs/contracts.md#trace-contract-v1)

### 3. Quyền lợi khác với số tiền được ghi

**Mục đích:** Chứng minh vì sao shape phải chuyển nguyên quote cho host.

| Claim | Chỉ trên màn hình | Ý nghĩa |
| --- | --- | --- |
| `C-007` | `denied`, quote **35.000**, ledger **0**, `approval_expired` | Có quyền lợi theo chính sách nhưng approval hết hạn, host ghi `policy_denied`. |
| `C-013` | `denied`, quote **35.000**, ledger **0**, `order_already_refunded` | Đơn đã được hoàn đủ qua claim trước. |
| `C-014` | `resolved`, quote **150.000**, ledger **120.000** | Host trừ khoản **30.000 VND** đã hoàn trước đó. |

**Nói:** «Nếu shape tự trừ khoản cũ trước khi gọi host, host sẽ trừ lần nữa. Quote là mức quyền lợi đầy đủ, ledger là tiền thực ghi sau phê duyệt và các mức trần.»

### 4. Crash và chạy lại

**Mục đích:** Cho thấy checkpoint ghi tiến độ còn ledger bảo vệ giao dịch khi chạy lại.

**Chỉ trên màn hình:** Phản ví dụ của đề in `unsafe refund rows: 2`. Sau đó `C-012` dừng đúng ở `after_effect_before_checkpoint`. Ngay sau crash có `refund=1`, `refund_committed=1`, `checkpoint=0`. Khi chạy lại trên **cùng SQLite**, checkpoint lên 1 và số giao dịch vẫn là 1. Crash suite chạy trực tiếp đạt **20/20**.

**Nói:** «Ở cửa sổ crash này, tiền và audit đã được ghi nhưng tiến độ chưa lưu. Khi chạy lại, host tìm thấy refund hiện có nhờ khóa `refund:{claim_id}`. Nó hoàn tất checkpoint mà không ghi thêm tiền.» [Báo cáo crash](../../src/reports/crash.json)

### 5. Benchmark và quyết định

**Mục đích:** So sánh bốn cách triển khai trên cùng 14 claim và 5 seed `11, 22, 33, 44, 55`, tổng cộng 280 lượt. Mỗi lượt có SQLite mới.

| Kiến trúc | Lượt đạt | Pass^5 | VND mô phỏng/lượt đạt |
| --- | ---: | ---: | ---: |
| Workflow | 70/70 | 100% | 27,86 |
| Single Agent | 70/70 | 100% | 32,92 |
| Orchestrator | 70/70 | 100% | 37,14 |
| Swarm | 69/70 | 92,86% | 49,57 |

**Nói:** «Pass rate đếm lượt đúng, còn Pass^5 đếm claim đúng ở cả năm seed. Workflow đồng hạng cao nhất về độ đúng và ổn định, với chi phí mô phỏng thấp nhất. Vì vậy ADR chọn Workflow. Số bước là sự kiện trace; latency là unavailable. Điểm hidden cần giảng viên chấm.» [Benchmark](../../src/reports/benchmark.json) · [ADR](decision_adr.md)

Nếu được yêu cầu chạy benchmark ngay tại chỗ, dùng `& $lab8Python -m scripts.demo_lab8 --section benchmark --live-benchmark`. Demo chạy lại 280 lượt và so nội dung với JSON đã lưu.

### 6. C-002 và bonus B3

**Mục đích:** Dùng cùng ticket và seed để chứng minh verifier sửa một quyết định sai ở bước chọn dữ kiện tính tiền.

**Chỉ trên màn hình:** Ticket nói **5 ngày**, dữ liệu đơn ghi **2 ngày**, ngưỡng là **3 ngày**. Với seed `55`, Swarm trả `resolved`, ghi **20.000 VND**. Workflow và `swarm_verified` trả `denied` với **0 VND**. Trace bonus ghi `verifier_override` cho `delay_days`.

**Nói:** «C-002 phù hợp làm ca hồi quy vì hai số ngày nằm hai phía của ngưỡng. Approval hợp lệ nên host có thể ghi số tiền đề xuất dù thông tin dùng để tính đã sai. Verifier đối chiếu dữ liệu trước khi ghi, phát hiện phần lệch và tính lại đúng một lần. Trên chín ca riêng, Swarm gốc đạt 42/45 lượt và bản có verifier đạt 45/45 lượt. Workflow vẫn rẻ hơn và đạt cùng độ đúng trong hai bộ đã đo.»

**Kết:** «Dữ liệu đơn và chính sách đủ cho nhiệm vụ này. Chúng em chọn Workflow và dùng bonus để kiểm chứng cách giữ an toàn cho kiến trúc có model.» [Research card](research_card.md) · [Báo cáo B3](bonus_report.md)

## Câu hỏi bảo vệ nhanh

| Câu hỏi | Trả lời ngắn |
| --- | --- |
| Vì sao Swarm qua 62 test mà benchmark báo 69/70? | Test public của Swarm có một ca kiểm tra lỗi mẫu phải xuất hiện. Benchmark tính theo kết quả nghiệp vụ đúng. |
| Vì sao host chấp nhận Swarm ở C-002? | Host áp phê duyệt, trần và chống trùng. `compute_compensation` ở shape tính quyền lợi trước đó, nên verifier cần kiểm tra nguồn dữ kiện làm quote. |
| Thử claim thiếu mã đơn hoặc sai chủ đơn thế nào? | `C-004` phải `needs_info`, `C-005` phải `escalated`, cả hai có ledger bằng 0. Có thể chạy từng ca bằng `lab8.run` và một `--db` mới. |
| Khi nào cân nhắc Orchestrator thay Workflow? | Khi nhiệm vụ có thông tin cần điều tra độc lập hoặc yêu cầu tách quyền, và benchmark trên dữ liệu đại diện cho thấy lợi ích đủ bù chi phí. |
| Có thể nói an toàn tuyệt đối hoặc đã qua hidden chưa? | Chỉ kết luận trong phạm vi dữ liệu đã đo. Crash suite, public và ca B3 đều có bằng chứng riêng; điểm hidden của giảng viên còn phải xác nhận. |

## Nếu gặp trục trặc trong lúc demo

- Nếu gõ sai lệnh, chạy lại với `--section` tương ứng. Demo dùng thư mục tạm mới mỗi lần.
- Nếu thiếu thư viện, xem [hướng dẫn cài đặt](../../src/README.md). `No module named scripts.demo_lab8` thường do đang đứng ngoài `src/`.
- Nếu thiếu thời gian cho benchmark chạy trực tiếp, dùng bảng đã lưu, rồi chạy live hai phần `crash` và `bonus`. Có thể mở thêm `b3.c002_trace_excerpt` trong [báo cáo B3 public](../../src/reports/bonus_b3_public.json).
- Kiểm tra trước khi nộp bằng `& $lab8Python -m lab8.check_submission`. Tại thời điểm soạn demo, mục còn thiếu là xác nhận thành viên và bảng đóng góp trong `TEAM.md`. Bài chỉ sẵn sàng nộp sau khi hoàn tất mục này và các báo cáo cá nhân.
