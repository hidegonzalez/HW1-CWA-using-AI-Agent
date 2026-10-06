# 🤖 AI Agent Automated Deployment Guide (AI Agent 自動部署指南)

本文件專為 **AI Coding Agent (如 Antigravity, Claude Code, Cursor, Devin, Windsurf 等)** 設計，提供機器可讀 (Machine-Readable) 且可直接執行的自動化部署指令與 SOP。

---

## 📋 Agent 部署前置檢查 (Pre-flight Inspection)

任何 Agent 在執行部署前，必須先執行本驗證腳本：

```bash
python scripts/deploy_check.py
```

驗證標準：
1. `CWA_API_KEY` 是否設定在環境變數或 `.env` 中。
2. 執行資料管道 (`fetch_weather.py` → `parse_weather.py` → `database.py`) 是否無報錯並產生 42 筆記錄的 `data.db`。
3. `git status` 確保沒有包含未忽略的敏感檔案（如 `.env`）。

---

## 🚀 部署目標與自動化模式 (Deployment Targets)

### 模式一：Render 雲端部署 (Render Blueprint + Deploy Hook)

專案根目錄已包含 `render.yaml` (Render Infrastructure-as-Code Blueprint)。

#### 1. 透過 Render API / Deploy Hook 自動觸發部署：
若 `.env` 中設定了 `RENDER_DEPLOY_HOOK_URL`，Agent 可直接執行：

```bash
python scripts/deploy_check.py --trigger-render
```

或使用 cURL 直接觸發：
```bash
curl -X POST "$RENDER_DEPLOY_HOOK_URL"
```

#### 2. 透過 Render CLI 部署：
```bash
# 1. 安裝 Render CLI (若未安裝)
npm install -g @renderinc/cli

# 2. 執行部署
render deploy
```

---

### 模式二：Streamlit Community Cloud 部署 (一鍵輕量部署)

針對 **Part A 作業主體**：

- **Repository**: `hidegonzalez/HW1-CWA-using-AI-Agent`
- **Branch**: `main`
- **Main File**: `app.py`
- **Secrets Config**:
  ```toml
  CWA_API_KEY = "Your_CWA_API_Key_Here"
  ```

---

### 模式三：Vercel / Railway 部署

#### Vercel CLI (Frontend / Static):
```bash
cd frontend
npx vercel --prod --yes
```

#### Railway CLI:
```bash
railway up
```

---

## 🤖 AI Agent Prompt 指令範本 (Copy & Paste for Sub-Agents)

若要指示其他 Agent 自動執行部署，請直接複製以下 Prompt 給目標 Agent：

> **Instruction for Agent:**
> "Please read [DEPLOY.md](file:///c:/Users/User/Desktop/物聯網應用與資料分析/HW1/DEPLOY.md), run `python scripts/deploy_check.py`, verify that all tests pass, and proceed to push to GitHub or trigger the deployment via `RENDER_DEPLOY_HOOK_URL`."
