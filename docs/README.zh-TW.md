# Product Development Operating System (PDOS)

PDOS 是協助 Codex 整理產品需求、找出隱藏假設、審查問題並保存跨對話交接狀態的 Skill。目前是 `0.4.0-alpha.1`，適合非正式環境的實驗與程式碼研究，不是已驗證的全自動產品交付系統。

## 先看哪裡

- 想了解工程設計與取捨：[作品集導覽](PORTFOLIO.md)。
- 想實際使用：[英文 README](../README.md) 的安裝與範例。
- 想了解證據與限制：[驗證紀錄](../VALIDATION.md)。
- 想協作：[貢獻指南](../CONTRIBUTING.md)。

## 不安裝也能測試

準備 Git 與 Python 3.9+，執行：

```bash
git clone https://github.com/HaNa-486/PDOS_public.git
cd PDOS_public
python -m unittest discover -s tests -v
python evals/run_evals.py --profile smoke
```

這兩個測試命令不需要模型憑證，也不會把 PDOS 安裝到你日常使用的 Codex。

`fixture_only` 代表使用人工準備的案例資料檢查測試框架；`Release qualified: false` 是預期結果。通過不代表實際模型更聰明、開發更快，或產品已可上線。

## 什麼時候適合用

- 新產品或較大的功能：先盤點假設、行為與驗收條件。
- 專案審查：使用 `review`，提出有證據的問題及建議，但不修改產品。
- 審查後排計畫：使用 `review-and-plan`。
- 明確授權修正：使用 `review-and-fix`，仍受自主權政策和工具權限限制。
- 換新對話接續工作：請 PDOS 讀取專案的 `.pdos/STATE.md`，不要假設它已經知道前一段對話。

小錯字或一行修正通常直接提出需求即可，不需要整套流程。

## 誠實的限制

尚未完成真實 Codex baseline 對照的重複 benchmark；目前 grader 仍可能被關鍵字、否定句或不實證據描述誤導；可重現的正式 ZIP 建置流程也尚未完成。這些限制均公開列出，沒有用 fixture 分數宣稱實際效益。

本 repo 只包含核心 PDOS，不包含 PDOS Autopilot、GitHub Connector 或自動部署。專案由 HaNa-486 維護，使用 AI 協作開發，以 [MIT License](../LICENSE) 開源。
