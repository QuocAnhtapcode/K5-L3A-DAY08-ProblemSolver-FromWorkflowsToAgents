# Team — Problem Solver

## Thông tin nhóm

- Tên nhóm: Nhóm demo - Problem Solver
- Lớp: L3A
- Repo nhóm: K5-L3A-DAY08-ProblemSolver-FromWorkflowsToAgents
- URL repo: https://github.com/QuocAnhtapcode/K5-L3A-DAY08-ProblemSolver-FromWorkflowsToAgents
- Nhánh: main.

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| ---: | --- | --- | --- | --- | --- |
| 1 | Hoàng Quốc Anh | 03707 | Chưa cung cấp | QuocAnhtapcode | Tech lead, workflow, tích hợp và B3 |
| 2 | Đỗ Thị Thanh Bình | 03709 | Chưa cung cấp | Chưa cung cấp | BA, luật nghiệp vụ, acceptance criteria và báo cáo |
| 3 | Lê Gia Hưng | 03713 | Chưa cung cấp | Chưa cung cấp | Single ReAct, QA, crash và retry |
| 4 | Hà Quang Vinh | 03720 | Chưa cung cấp | Chưa cung cấp | Orchestrator, handoff, benchmark và HTML |

## Bảng đóng góp

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| 03707 — Hoàng Quốc Anh | Tech lead, workflow, tích hợp và B3 (phân công nghiệm thu) | Snapshot source_sha256_lf trong src/reports/hidden_summary.json; chưa chốt commit | src/tests/test_workflow_requirements.py; test_bonus_b3.py; test_submission_portability.py |
| 03709 — Đỗ Thị Thanh Bình | BA, luật nghiệp vụ, acceptance criteria và báo cáo (phân công nghiệm thu) | Snapshot source_sha256_lf trong src/reports/hidden_summary.json; chưa chốt commit | src/tests/test_workflow_requirements.py; test_verified_matches_handwritten_adversarial_labels trong test_bonus_b3.py |
| 03713 — Lê Gia Hưng | Single ReAct, QA, crash và retry (phân công nghiệm thu) | Snapshot source_sha256_lf trong src/reports/hidden_summary.json; chưa chốt commit | src/tests/test_single_agent.py; test_verified_crash_replay_and_audit trong test_bonus_b3.py |
| 03720 — Hà Quang Vinh | Orchestrator, handoff, benchmark và HTML (phân công nghiệm thu) | Snapshot source_sha256_lf trong src/reports/hidden_summary.json; chưa chốt commit | src/tests/test_orchestrator_boundary.py; test_submission_portability.py; test_bonus_b3.py |

## Cá nhân

- [03707 — Hoàng Quốc Anh](report/team/03707_HoangQuocAnh.md)
- [03709 — Đỗ Thị Thanh Bình](report/team/03709_DoThiThanhBinh.md)
- [03713 — Lê Gia Hưng](report/team/03713_LeGiaHung.md)
- [03720 — Hà Quang Vinh](report/team/03720_HaQuangVinh.md)

## Bằng chứng nghiệm thu hidden

Hidden local: workflow 200/200 trial, pass rate 1.0000, pass⁵ 1.0000, variance 0.000000, 29.00 VND mô phỏng/success. Báo cáo chi tiết ở [hidden_validation.md](report/team/hidden_validation.md).
