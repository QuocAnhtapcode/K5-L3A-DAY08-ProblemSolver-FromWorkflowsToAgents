# Bàn giao Lab09 — Problem Solver

Nguồn đề: https://github.com/VinUni-AI20k/K5-Day9-Evaluation-and-Failure-Analysis
Lab08 parent: `464ad8a274f074ae897d7660b0d49adc5532a55f`. Lab09 được bổ sung trong bản clone riêng; `src/lab8/` giữ nguyên.

Code, test, phân tích trace và tài liệu Lab09 được hỗ trợ bằng Codex. Số liệu lấy từ lệnh chạy thực tế và log; chưa xác nhận đóng góp cá nhân hay phê duyệt của các thành viên. Nguồn code nền, dữ liệu, variant và trap: starter của VinUni-AI20k được dẫn ở trên.

Tái lập từ gốc repo:

```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r src/requirements.txt -r src/requirements-lab9.txt
./.venv/Scripts/python.exe scripts/reproduce_lab9.py
```

- M0/M1: smoke; v1 14 item và v2 28 item, labels tách riêng, provenance và taxonomy; 5 anchor ở src/reports/coding_sheet.csv.
- M2: tone đạt, helpful bị loại; 5 bất đồng được đối chiếu rubric CSV, không giả nhận có nhãn người mới.
- M3: ApprovalBypass, RefundAmountCorrect, ReplyLedgerConsistent; test trace case C-002@11.
- M4: fixed merge, seeded_regression block; pass_rate Δ −0.271, CI [−0.500, −0.057].
- M5–M7: mapping đủ, slice gate, pass@k/pass^k, integrity và ratchet; scorecard public 3/3, 0 false alarm; 4 trap bị chặn.

Báo cáo chi tiết: [eval card](eval_card.md), [PRD](PRD_v1.1.md), [taxonomy](failure_taxonomy.md), [judge audit](judge_audit.md), [trace case](trace_case.md).

Theo lựa chọn của chủ repo, phạm vi bàn giao là bản local. Đã chuẩn bị CI, evidence và nội dung PR; chưa push/mở PR, chưa có kết quả GitHub Actions hay hidden grader.
README/CHECKPOINTS/RUBRIC/SUBMISSION/.gitignore ở gốc giữ của Lab08 theo yêu cầu overlay; đề Lab09 đọc ở bản clone lab9-starter.
