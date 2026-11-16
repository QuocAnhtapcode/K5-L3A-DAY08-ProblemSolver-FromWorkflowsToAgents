# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 1e98073
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 100% (70/70 lượt) / 100% (14/14 claim đạt cả 5 seed) / 100%–100% / 0
- Cost per success (mô phỏng, VND): 27,86 VND/lượt đạt (1.950 VND mô phỏng chia 70 lượt đạt)
- Crash safety: 20/20 (crash suite chính thức); Workflow qua T11 và T12 trong ma trận public
- Secret leak / approval bypass: 0 / 0 được phát hiện trong 70 lượt public của Workflow theo kiểm tra trace, kết quả và ledger đối chiếu với nhãn public

## Vì sao shape này

Chọn Workflow vì dữ liệu đơn hàng và chính sách hiện hành đủ để xử lý bài toán hoàn tiền theo các bước Python cố định. `compute_compensation` tính mức đề xuất từ dữ liệu có cấu trúc. Workflow gửi nguyên mức đề xuất cho `durability.issue_refund` để host kiểm phê duyệt đúng claim, áp trần theo đơn, trừ phần đã hoàn và chống ghi trùng khi chạy lại. Benchmark ghi nhận Workflow dùng 0 lượt gọi model.

Trên cùng 14 claim public, 5 seed `11, 22, 33, 44, 55` và cùng bảng giá, Workflow, Single Agent và Orchestrator đều đạt 70/70 lượt, pass^5 100% và phương sai 0. Chi phí mô phỏng mỗi lượt đạt lần lượt là 27,86, 32,92 và 37,14 VND. Swarm đạt 69/70 lượt, pass^5 92,86%, phương sai theo seed 0,000816 và chi phí 49,57 VND/lượt đạt. Swarm sai ở `C-002`, seed `55`, vì dùng số ngày trễ từ ticket thay cho dữ liệu đơn hàng. Kết quả public ủng hộ việc giữ luồng ít tự chủ nhất trong các kiến trúc đạt 70/70 lượt. [Báo cáo benchmark](../../src/reports/benchmark.json)

## Có đáng đổi lấy multi-agent không

Giữ Workflow cho tập claim hiện tại vì Single Agent và Orchestrator chưa cho thấy cải thiện về độ đúng hay độ ổn định, còn chi phí mô phỏng cao hơn. Cân nhắc đổi nếu bài toán có thêm các bước điều tra độc lập hoặc cần tách quyền theo vai trò, và benchmark trên bộ claim đại diện cho nhu cầu mới cho thấy lợi ích về tỷ lệ đạt hoặc pass^5 đủ bù chi phí. Kiến trúc mới vẫn phải qua các cổng phê duyệt, rò rỉ dữ liệu và khôi phục sau crash.

## Trace và bằng chứng

Workflow ghi `get_claim_view`, `lookup_order`, `compute_compensation`, `issue_refund` và `decision` khi chạy qua các bước tương ứng. Trace chỉ lưu các cờ tra cứu, lý do trả về của công cụ, mức đề xuất và trạng thái. Trace bỏ nội dung ticket, nguyên bản ghi claim hoặc đơn hàng, `parent_secret`, header, số điện thoại, địa chỉ, tên hàng và ghi chú nội bộ.

Run `R-workflow-C-001-s11` có `status=resolved` và `passed=true` trong benchmark. Báo cáo crash ghi 20/20 ca đạt, trong đó `CR-19` kiểm tra thử lại khi thiếu phê duyệt. Bộ crash chính thức chủ yếu kiểm tra host và có một ca dành cho Swarm. T11 và T12 trong ma trận public là bằng chứng trực tiếp bổ sung cho việc chạy lại và khôi phục của Workflow. [Báo cáo crash](../../src/reports/crash.json) · [Ma trận public](../../src/tests/test_public_matrix.py)

Để kiểm chứng trace, scanner cần đọc được `trace_path` của lần chạy hiện tại và các file `<run_id>*` cùng thư mục. Artefact nằm ngoài phạm vi quét cần được đưa vào nơi scanner đọc được, rồi quét lại cùng kết quả và kiểm tra cả stdout nếu có. Thiếu trace, trace cũ, sai định dạng hoặc lệch `run_id` làm lượt chấm thất bại. [Hợp đồng trace](../../docs/contracts.md#trace-contract-v1)

## Giới hạn

Kết luận dựa trên 14 claim public và MockLLM. Chi phí dùng bảng giá mô phỏng và latency là `unavailable`. Repo chưa có `student_drop` để tự kiểm và ngưỡng pass rate hidden ≥ 75% vẫn cần được giảng viên xác nhận. Các số liên quan đến trace và phê duyệt ở trên chỉ áp dụng cho các lượt public đã kiểm tra.
