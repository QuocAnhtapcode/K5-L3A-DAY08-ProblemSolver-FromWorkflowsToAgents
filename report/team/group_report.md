# Báo cáo nhóm — Lab 8 LogiX-VN

## 1. Thông tin nhóm

- Nhóm ProblemSolver, lớp L3A.
- Thành viên và bằng chứng đóng góp được kê khai trong [TEAM.md](../../TEAM.md).
- Commit chốt: 8bc7bbc (trùng [ADR](decision_adr.md)).

## 2. Mục tiêu và cách tiếp cận

Xử lý cùng một yêu cầu hoàn tiền LogiX-VN bằng bốn kiến trúc và dùng kết quả đo để chọn mức tự chủ phù hợp. Workflow được triển khai trước để chốt luồng nghiệp vụ, sau đó thêm Single Agent và Orchestrator. Swarm là bản tham chiếu do đề cung cấp. Bốn shape dùng cùng dữ liệu đơn hàng, chính sách, cổng duyệt và hợp đồng kết quả. Test public được chạy riêng sau mỗi triển khai.

## 3. Giải pháp

| Kiến trúc | Cách đọc và quyết định |
| --- | --- |
| Workflow | Dùng bước Python cố định để đọc claim, tra đơn theo quyền của principal và gọi `compute_compensation`. Không gọi model. |
| Single Agent | `run_react` giới hạn 8 bước. MockLLM chọn tool đọc hợp lệ, trong đó có thể tra thêm lịch sử hoàn tiền. Tiền do `compute_compensation` tính. |
| Orchestrator | `make_handoff` tạo gói `handoff.v1` theo allowlist. Investigator chỉ được tra `lookup_order` trong phạm vi principal. Orchestrator tính quote từ dữ liệu đã tra. |
| Swarm | Dùng bản có sẵn để đối chứng. Nhánh tham chiếu ở seed chia hết cho 5 có thể tin số ngày trễ lấy từ ticket. |

Ở cả bốn shape, host nhận **quote đầy đủ** để áp phê duyệt đúng claim, trần theo đơn, khoản đã hoàn trước đó và khóa chống ghi trùng. Ví dụ T14 đề xuất 150.000 VND trong khi host chỉ ghi 120.000 VND vì đã hoàn 30.000 VND ở claim trước. Trace ghi quyết định và dữ kiện kỹ thuật cần kiểm tra, giữ ngoài trace nội dung ticket, bản ghi thô, secret, header và PII. Handoff của Orchestrator chỉ cấp `lookup_order`. [Luật nghiệp vụ](../../docs/business_rules.md) · [Hợp đồng kết quả và trace](../../docs/contracts.md)

## 4. Kết quả

Benchmark dùng cùng 14 claim, 5 seed `11, 22, 33, 44, 55` và SQLite mới cho từng lượt. Chi phí là VND mô phỏng mỗi lượt đạt. Số bước là số sự kiện trace.

| Shape | Lượt đạt | Pass rate | Pass^5 | Min–max theo seed | Phương sai | Chi phí/lượt đạt | Bước TB / p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Workflow | 70/70 | 100% | 100% | 100%–100% | 0 | 27,86 | 4,43 / 5 |
| Single Agent | 70/70 | 100% | 100% | 100%–100% | 0 | 32,92 | 5,97 / 8 |
| Orchestrator | 70/70 | 100% | 100% | 100%–100% | 0 | 37,14 | 5,36 / 6 |
| Swarm | 69/70 | 98,57% | 92,86% | 92,86%–100% | 0,000816 | 49,57 | 2,80 / 3 |

Chọn Workflow vì đồng hạng cao nhất về độ đúng và ổn định, đồng thời có chi phí thấp nhất. Crash suite chính thức đạt **20/20**. Cả ba shape đã qua T11 và T12 trong ma trận public. Bộ test đầy đủ đạt **308/308**, gồm ba ca kiểm tra phê duyệt thuộc claim khác khi chạy lại và ba test bonus B3. Hai báo cáo chính thức được chạy lại và định dạng JSON tái tạo trùng từng byte. [Benchmark](../../src/reports/benchmark.json) · [Crash suite](../../src/reports/crash.json) · [Test tích hợp](../../src/tests/test_student_shapes_approval_binding.py)

Thí nghiệm R2 kiểm tra lỗi `R-swarm-C-002-s55`. Khi tính tiền chỉ từ số ngày trong dữ liệu đơn, Swarm tăng từ 69/70 lên 70/70 lượt đạt, với chi phí/lượt đạt giảm từ 49,57 xuống 48,72 VND mô phỏng. [Research card](research_card.md)

Bonus B3 thêm verifier trước bước ghi. Swarm có verifier đạt 70/70 trên bộ public và 45/45 trên chín ca đối kháng, với chi phí lần lượt 48,86 và 53,84 VND mô phỏng mỗi lượt đạt. Workflow vẫn rẻ hơn trên cả hai bộ. [Báo cáo B3](bonus_report.md)

## 5. Khó khăn và cách xử lý

- Trên Windows, lượt kiểm tra ban đầu gặp `PermissionError: [WinError 5]` ở thư mục tạm mặc định của pytest. Chạy lại với `--basetemp` trỏ tới thư mục mới đã giải quyết lỗi thiết lập fixture.
- Bộ lọc `-k single` cũng khớp tên `test_public_single_run_cases` của tất cả shape. Khi cần chạy riêng Single Agent, dùng `python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"` để chọn đúng 62 test.

## 6. Tổng hợp đóng góp

Bảng đóng góp trong `TEAM.md` và các báo cáo cá nhân là nơi ghi công việc thực tế, commit, test và cách từng thành viên tự xác minh kết quả. Codex đã hỗ trợ triển khai, chạy kiểm thử và soạn tài liệu kỹ thuật cho phần làm chung.

## 7. Hạn chế và hướng cải thiện

Kết quả chỉ áp dụng cho 14 claim public với MockLLM. Latency là `unavailable`, điểm hidden chưa có và repo chưa có `student_drop`. So sánh chi phí phụ thuộc bảng giá mô phỏng và số lần gọi công cụ. Số sự kiện trace phụ thuộc mức chi tiết của từng shape. Chỉ cân nhắc tăng mức tự chủ nếu nhiệm vụ mới có các bước điều tra độc lập hoặc cần chia quyền, và dữ liệu đại diện cho thấy lợi ích đủ bù chi phí.

## 8. Tài liệu tham khảo

- [Mô tả đề Lab 8](../../README.md), [kiến trúc](../../docs/architecture.md) và [định nghĩa metric](../../docs/metrics.md).
- Cemri và cộng sự (2025), [*Why Do Multi-Agent LLM Systems Fail?*](https://proceedings.neurips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html), NeurIPS Datasets and Benchmarks Track.
