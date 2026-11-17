# Trace case — C-002@11

| Trường | Bằng chứng |
|---|---|
| Trial/report | `seeded_regression C-002@11`, report `E-seeded_regression-20261117-632e` |
| Triệu chứng | Ledger 20000 VND, nhãn 0; status resolved thay vì denied; RefundAmountCorrect và TrialPass fail |
| Bước sai đầu tiên | Event 3, `model_override`, `delay_days=5` |
| Các bước trước | Handoff chỉ có allowlist; investigator đọc order O-202 có delay_days=2, policy hiện hành; chưa có dữ kiện sai ở các event trước 3 |
| Failure mode | FM-03: lời khách nói 5 ngày đè DB 2 ngày, làm phát sinh quyền hoàn tiền không có thật |
| Đối chứng fixed | Không có model_override, ledger 0 VND, status denied, grader PASS |
| Regression test | `tests/test_lab9_regressions.py::test_lab9_trace_case_first_wrong_step_ticket_over_db` kiểm override, ledger grader fail trên bản lỗi và pass trên fixed |
| Giới hạn | Trace không chứng minh suy nghĩ nội tại; event không phải điều kiện bắt buộc để bắt lỗi, vì quiet_override có thể không phát event |

Tái lập: `python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11` và cùng lệnh với `--shape fixed`.
