# Research card

Phiếu này ghi lại thí nghiệm R2 trên bản Swarm do lab cung cấp. Hai lượt chạy dùng cùng trình chấm public.

## Phiếu của nhóm

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2 · Phân loại lỗi kiểm chứng |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Cemri và cộng sự, *Why Do Multi-Agent LLM Systems Fail?*, NeurIPS 2025. Nghiên cứu thực nghiệm dựa trên các trace được gán nhãn. [Kỷ yếu](https://proceedings.neurips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html) · [Bản đầy đủ, Hình 1 và Phụ lục A.3](https://proceedings.neurips.cc/paper_files/paper/2025/file/b1041e52d3be19f0a9bc491657488e4a-Paper-Datasets_and_Benchmarks_Track.pdf) |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | MAST phân loại 14 kiểu lỗi thành ba nhóm và xếp lỗi kiểm chứng thiếu hoặc sai vào nhóm kiểm chứng nhiệm vụ. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | MAST lấy bằng chứng từ hơn 1.600 trace của 7 framework đa agent trong các tác vụ như lập trình, toán và agent tổng quát. LogiX-VN dùng 14 claim giả lập và MockLLM. Nhãn FM-3.3 cho C-002 là cách áp dụng taxonomy vào ca lab. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Nếu khóa số ngày trễ dùng để tính tiền về dữ liệu đơn, dự kiến sửa đúng một lỗi đã thấy ở C-002 seed 55. Pass rate dự kiến tăng từ 69/70 lên 70/70, khoảng 1,43 điểm phần trăm. Đây là giả thuyết giải thích một lỗi public đã biết. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi | Chạy cùng Swarm hai lần trên 14 claim × 5 seed, cùng MockLLM, danh sách công cụ, dữ liệu, bảng giá và evaluator. Biến duy nhất là số ngày suy ra từ ticket có được đưa vào nhánh tính quote hay không. Chế độ verified chặn đầu vào đó riêng tại nhánh tính tiền. Lời gọi parse của MockLLM vẫn chạy ở cả hai chế độ. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | C-002 seed 55 có ngày trễ trong ticket khác dữ liệu đơn. Kiểm tra trạng thái cuối của cùng run ID, rồi so pass rate, pass^5, phương sai và chi phí mô phỏng mỗi lượt đạt. |

## Kết quả ablation

Chạy trong `src/` với Python đã cài thư viện của lab.

```powershell
python -m scripts.research_swarm_verification --mode baseline --out reports/research_swarm_baseline.json
python -m scripts.research_swarm_verification --mode verified --out reports/research_swarm_verified.json
```

| Chế độ | Lượt đạt | Pass^5 | Phương sai theo seed | VND mô phỏng/lượt đạt |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 69/70 | 92,86% | 0,000816 | 49,57 |
| Verified | 70/70 | 100% | 0 | 48,72 |

Giả thuyết được dữ liệu public ủng hộ. Chỉ cặp C-002 seed 55 đổi kết quả: từ `resolved` sai sang `denied` đúng. Run ID là `R-swarm-C-002-s55` trong cả hai file, nên cần đọc cùng tên báo cáo. Số lượt gọi model giữ nguyên ở từng trial. Ở ca đổi kết quả, số tool call giảm từ 6 xuống 5 vì bỏ lần tính lại quote từ số ngày trong ticket. [Baseline JSON](../../src/reports/research_swarm_baseline.json) · [Verified JSON](../../src/reports/research_swarm_verified.json) · [Script](../../src/scripts/research_swarm_verification.py)

Kết quả giải thích lỗi của một bản tham chiếu trên bộ public. Thí nghiệm dùng MockLLM, chi phí mô phỏng và latency `unavailable`. Cần dữ liệu độc lập để kiểm tra kết luận có lặp lại ở các ca khác hay không.
