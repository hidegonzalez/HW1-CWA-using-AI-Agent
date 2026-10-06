# CWA 台灣天氣預報與即時觀測中樞 (AIoT HW1)

本專案包含作業核心 (Part A) 與進階互動儀表板 (Part B)：

- **Part A（作業標準要求）**：使用 Python 抓取 CWA 氣象資料、解析並儲存至 SQLite (`data.db`)，並由 Streamlit 讀取 SQLite 呈現互動式表格、折線圖與 Folium 台灣平均氣溫地圖。
- **Part B（Part 5 高階圖層）**：使用 FastAPI 做為後端 API，前端採用 Vite + React + TypeScript + Windy Map API + Leaflet，實現全圖層氣溫點位標記、熱力圖切換與歷史快照時間滑桿。

---

## 🛠️ 環境設定與安裝

1. **建立 Python 虛擬環境並安裝套件**：
   ```bash
   python -m venv venv
   # Windows PowerShell:
   .\venv\Scripts\activate
   pip install -r requirements.txt fastapi "uvicorn[standard]" httpx pydantic
   ```

2. **設定環境變數**：
   複製 `.env.example` 為 `.env`，並填入授權金鑰：
   ```ini
   CWA_API_KEY=你的CWA開放資料授權碼
   WINDY_API_KEY=你的WindyMapAPI金鑰
   ```

---

## 🚀 執行方式

### 模式一：獨立執行 Part A (Streamlit 作業本體)

依序執行以下步驟即可建立資料庫並啟動 Streamlit：

```bash
# 1. 抓取氣象署預報資料 (預設自動回退至 F-D0047-091)
python fetch_weather.py

# 2. 解析 JSON 並彙整六大分區每日最高與最低氣溫
python parse_weather.py

# 3. 匯入至 SQLite 資料庫 (data.db) 並執行驗證查詢
python database.py

# 4. 啟動 Streamlit Web App
streamlit run app.py
```
开启瀏覽器前往 `http://localhost:8501` 即可查看作業成果。即使未開啟 Part B，Part A 的選單、SQLite 折線圖與 Folium 台灣地圖均可完整獨立運作。

---

### 模式二：同時啟動 Part B (完整一體化動態儀表板)

若欲體驗整合了 Windy 動態風場與熱力圖的完整介面：

1. **啟動 FastAPI 後端** (Port 8000)：
   ```bash
   uvicorn backend.app.main:app --port 8000 --reload
   ```

2. **啟動 React 前端** (Port 5173)：
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **啟動 Streamlit 總儀表板** (Port 8501)：
   ```bash
   streamlit run app.py
   ```
前往 `http://localhost:8501`，Streamlit 將會自動偵測並無縫嵌入 Windy 即時動態地圖，達成點擊折線圖、切換區域與 Windy 地圖雙向連動的效果。

---

## 📂 專案架構說明

- `fetch_weather.py`：使用 `requests` 加載 headers Authorization 取得 CWA API 資料並儲存原始 JSON。
- `parse_weather.py`：解析 JSON，計算六大分區（北部、中部、南部、東北部、東部、東南部）包含的所有縣市平均氣溫，精確保留 7 天完整預報。
- `database.py`：建立 `TemperatureForecasts` SQLite 資料庫 (`data.db`)，並包含驗證 SQL 語句。
- `app.py`：Streamlit Web App 主程式，由 SQLite 進行 SQL 參數化查詢，提供互動圖表、Folium 地圖與可選的 Windy 整合。
- `backend/`：FastAPI 後端，負責 CWA 自動氣象站 (O-A0001-001) 即時資料與歷史快照 (`history.db`)。
- `frontend/`：Vite + React 前端，負責 Windy 地圖、Leaflet 測站圖層與時間滑桿。
