"""Step 4 + 5：Streamlit 氣溫預報 Web App（作業圖卡 4、5）

一體化畫面：
  ┌ 標題
  ├ Windy 即時地圖（Part B 前端，有啟動才嵌入；沒啟動時自動隱藏，不影響作業功能）
  ├ 下拉選單選擇地區 → 使用 SQL 從 SQLite 查詢 → 一週表格 + 最高/最低溫折線圖
  └ Folium 台灣地圖：各區域當日平均溫度（點折線圖可切換日期，同步 Windy 地圖時間）

所有預報數據都從 data.db 以 SQL 查詢，不直接呼叫 API。
"""
import os
import socket
import sqlite3

import altair as alt
import folium
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

DB_PATH = "data.db"
WINDY_FRONTEND_URL = os.getenv("WINDY_FRONTEND_URL", "http://localhost:5173")

# 如果雲端部署時尚無 data.db，自動執行資料管道產生
if not os.path.exists(DB_PATH):
    try:
        import fetch_weather, parse_weather, database
        fetch_weather.main()
        parse_weather.parse_weather()
        _conn = database.init_db()
        database.populate_db(_conn)
        _conn.close()
    except Exception as _e:
        print(f"Auto DB init warning: {_e}")

REGIONS_HOST_PORT = ("localhost", 5173)

REGION_ORDER = ["北部地區", "中部地區", "南部地區", "東北部地區", "東部地區", "東南部地區"]

# Windy iframe 的視角（選地區時地圖移過去）
WINDY_VIEW = {
    "北部地區": {"lat": 25.0330, "lon": 121.5654, "zoom": 9},
    "中部地區": {"lat": 24.1477, "lon": 120.6736, "zoom": 9},
    "南部地區": {"lat": 22.9997, "lon": 120.2270, "zoom": 9},
    "東北部地區": {"lat": 24.7523, "lon": 121.7584, "zoom": 9},
    "東部地區": {"lat": 23.9778, "lon": 121.6033, "zoom": 9},
    "東南部地區": {"lat": 22.7972, "lon": 121.0714, "zoom": 9},
}
TAIWAN_VIEW = {"lat": 23.6978, "lon": 120.9605, "zoom": 7}

# Folium 地圖上各區域標記的位置
REGION_MARKER = {
    "北部地區": (24.95, 121.35),
    "中部地區": (24.10, 120.75),
    "南部地區": (22.95, 120.40),
    "東北部地區": (24.65, 121.72),
    "東部地區": (23.75, 121.45),
    "東南部地區": (22.80, 121.08),
}

st.set_page_config(page_title="AIoT Taiwan Weather", page_icon="☀️", layout="wide",
                   initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }
    .title-container {
        text-align: center;
        padding-top: 20px;
        padding-bottom: 10px;
        margin-bottom: 0;
        font-family: sans-serif;
        font-weight: 900;
        font-size: 2.5rem;
        line-height: 1.5;
    }
    .title-grad {
        background: -webkit-linear-gradient(45deg, #0e81c4, #27c1f8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
    }
    iframe { border: none !important; }
    .legend-box {
        background: #1e1e1e; border: 1px solid #333; border-radius: 10px;
        padding: 14px 16px; line-height: 2; font-size: 0.95rem;
    }
    .legend-dot {
        display: inline-block; width: 14px; height: 14px; border-radius: 50%;
        margin-right: 8px; vertical-align: middle;
    }
    .info-card {
        background: linear-gradient(135deg, #17324a, #1e1e1e); border: 1px solid #2a4a66;
        border-radius: 10px; padding: 14px 16px; margin-top: 12px; line-height: 1.9;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="title-container">☀️ <span class="title-grad">AIoT 台灣天氣預測中樞</span></h1>',
            unsafe_allow_html=True)
st.markdown('<div class="subtitle">即時氣溫觀測 × Windy 動態風場 × 一週預報 (Streamlit &amp; SQLite Powered)</div>',
            unsafe_allow_html=True)


# ---------------------------------------------------------------- SQL 查詢
def query(sql: str, params: tuple = ()) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(sql, conn, params=params)


@st.cache_data(ttl=600)
def get_regions() -> list[str]:
    df = query("SELECT DISTINCT regionName FROM TemperatureForecasts")
    found = df["regionName"].tolist()
    return [r for r in REGION_ORDER if r in found] + [r for r in found if r not in REGION_ORDER]


@st.cache_data(ttl=600)
def get_region_forecast(region: str) -> pd.DataFrame:
    return query(
        "SELECT dataDate, mint, maxt FROM TemperatureForecasts "
        "WHERE regionName = ? ORDER BY dataDate LIMIT 7",
        (region,),
    )


@st.cache_data(ttl=600)
def get_day_all_regions(date: str) -> pd.DataFrame:
    return query(
        "SELECT regionName, mint, maxt, ROUND((mint + maxt) / 2.0, 1) AS avgt "
        "FROM TemperatureForecasts WHERE dataDate = ?",
        (date,),
    )


def windy_running() -> bool:
    if "localhost" not in WINDY_FRONTEND_URL and "127.0.0.1" not in WINDY_FRONTEND_URL:
        return True
    try:
        with socket.create_connection(REGIONS_HOST_PORT, timeout=0.3):
            return True
    except OSError:
        return False


def temp_color(t: float) -> str:
    if t < 20:
        return "#2f80ed"   # 藍
    if t < 25:
        return "#27ae60"   # 綠
    if t < 30:
        return "#f2c94c"   # 黃
    return "#eb5757"       # 紅


# ---------------------------------------------------------------- 版面
map_container = st.container()   # Windy 地圖放最上面，等知道地區/日期後再產生
st.markdown("<br>", unsafe_allow_html=True)

try:
    regions = get_regions()
except Exception:
    regions = []

selected_region = None
selected_date = None

_, main, _ = st.columns([1, 10, 1])
with main:
    if not regions:
        st.warning("data.db 中沒有預報資料，請依序執行 `fetch_weather.py` → `parse_weather.py` → `database.py`。")
    else:
        st.subheader("📊 區域一週預報趨勢 (SQLite)")
        c_left, c_right = st.columns([1, 2])

        with c_left:
            selected_region = st.selectbox("選擇預報地區", regions)
            df_region = get_region_forecast(selected_region)

            m1, m2, m3 = st.columns(3)
            m1.metric("本週最高", f"{df_region['maxt'].max():.1f}℃")
            m2.metric("本週最低", f"{df_region['mint'].min():.1f}℃")
            m3.metric("平均溫差", f"{(df_region['maxt'] - df_region['mint']).mean():.1f}℃")

            st.dataframe(
                df_region.rename(columns={"dataDate": "Date", "mint": "MinT", "maxt": "MaxT"}),
                use_container_width=True,
                hide_index=True,
            )

        with c_right:
            st.markdown(
                "<p style='text-align:center;font-size:0.9em;color:#888;'>"
                "💡 點選折線圖上的資料點，下方台灣地圖與上方 Windy 地圖都會切換到該日！</p>",
                unsafe_allow_html=True,
            )
            source = df_region.melt("dataDate", var_name="Type", value_name="Temp")
            source["Type"] = source["Type"].map({"maxt": "最高溫 MaxT", "mint": "最低溫 MinT"})

            click = alt.selection_point(name="click", fields=["dataDate"])
            chart = (
                alt.Chart(source)
                .mark_line(point=alt.OverlayMarkDef(size=90, filled=True))
                .encode(
                    x=alt.X("dataDate:O", title="日期"),
                    y=alt.Y("Temp:Q", title="溫度 (℃)", scale=alt.Scale(zero=False)),
                    color=alt.Color(
                        "Type:N",
                        scale=alt.Scale(domain=["最高溫 MaxT", "最低溫 MinT"], range=["#FF4B4B", "#0068C9"]),
                        legend=alt.Legend(title=None, orient="top"),
                    ),
                    opacity=alt.condition(click, alt.value(1.0), alt.value(0.25)),
                    tooltip=[alt.Tooltip("dataDate", title="日期"), alt.Tooltip("Type", title="類型"),
                             alt.Tooltip("Temp", title="溫度")],
                )
                .add_params(click)
                .properties(height=300, title=f"Temperature Forecast – {selected_region}")
            )
            event = st.altair_chart(chart, on_select="rerun", use_container_width=True,
                                    key=f"chart_{selected_region}")
            try:
                picked = event.selection.get("click") or []
                if picked:
                    selected_date = picked[0].get("dataDate")
            except AttributeError:
                pass

        dates = df_region["dataDate"].tolist()
        if selected_date not in dates:
            selected_date = dates[0]

        # ------------------------------------------------ 進階：Folium 台灣地圖
        st.subheader(f"🗺️ 台灣地圖：各區域平均溫度（{selected_date}）")
        day = get_day_all_regions(selected_date)

        g_map, g_side = st.columns([3, 1])
        with g_map:
            fmap = folium.Map(location=[23.75, 120.95], zoom_start=7, tiles="OpenStreetMap",
                              control_scale=True)
            for _, row in day.iterrows():
                pos = REGION_MARKER.get(row["regionName"])
                if not pos:
                    continue
                color = temp_color(row["avgt"])
                is_sel = row["regionName"] == selected_region
                popup = (f"<b>{row['regionName']}</b><br>Date: {selected_date}<br>"
                         f"Min: {row['mint']:.1f}°C<br>Max: {row['maxt']:.1f}°C<br>"
                         f"Avg: {row['avgt']:.1f}°C")
                folium.CircleMarker(
                    location=pos, radius=22 if is_sel else 16,
                    color="#ffffff" if is_sel else color, weight=4 if is_sel else 2,
                    fill=True, fill_color=color, fill_opacity=0.85,
                    popup=folium.Popup(popup, max_width=220),
                    tooltip=f"{row['regionName']} {row['avgt']:.1f}°C",
                ).add_to(fmap)
                folium.Marker(
                    location=(pos[0], pos[1] + 0.32),
                    icon=folium.DivIcon(
                        icon_size=(120, 24), icon_anchor=(0, 12),
                        html=(f"<div style='font-weight:700;font-size:13px;color:#222;"
                              f"text-shadow:0 0 3px #fff,0 0 3px #fff;'>"
                              f"{row['regionName'].replace('地區', '')} {row['avgt']:.1f}°</div>"),
                    ),
                ).add_to(fmap)
            components.html(fmap.get_root().render(), height=520)

        with g_side:
            st.markdown(
                "<div class='legend-box'><b>依平均溫度設定顏色</b><br>"
                "<span class='legend-dot' style='background:#2f80ed'></span>&lt; 20°C（藍色）<br>"
                "<span class='legend-dot' style='background:#27ae60'></span>20 – 25°C（綠色）<br>"
                "<span class='legend-dot' style='background:#f2c94c'></span>25 – 30°C（黃色）<br>"
                "<span class='legend-dot' style='background:#eb5757'></span>&gt; 30°C（紅色）</div>",
                unsafe_allow_html=True,
            )
            sel = day[day["regionName"] == selected_region]
            if not sel.empty:
                r = sel.iloc[0]
                st.markdown(
                    f"<div class='info-card'><b>{selected_region}</b><br>"
                    f"Date: {selected_date}<br>Min: {r['mint']:.1f}°C<br>Max: {r['maxt']:.1f}°C</div>",
                    unsafe_allow_html=True,
                )

# ---------------------------------------------------------------- Windy 即時地圖（Part B）
with map_container:
    if windy_running():
        target = WINDY_VIEW.get(selected_region, TAIWAN_VIEW)
        base_url = WINDY_FRONTEND_URL.rstrip('/')
        url = f"{base_url}?lat={target['lat']}&lon={target['lon']}&zoom={target['zoom']}"
        if selected_date:
            url += f"&time={selected_date}"
        components.iframe(url, height=750, scrolling=False)
    else:
        st.info("🌬️ Windy 即時觀測地圖未啟動（Part B，選用）。啟動方式見 README；下方一週預報與台灣地圖不受影響。",
                icon="ℹ️")
