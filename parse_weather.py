"""Step 2：分析 JSON，提取每日最高與最低氣溫（作業圖卡 2）

JSON 結構（F-D0047-091）：
records
 └ Locations[0]
    └ Location[]            ← 22 縣市（相當於規格中的 location）
       └ WeatherElement[]   ← 天氣要素
          ├ ElementName: 最低溫度 (MinT) → Time[].ElementValue[0].MinTemperature
          └ ElementName: 最高溫度 (MaxT) → Time[].ElementValue[0].MaxTemperature

處理方式：
  1. 每個縣市的預報是 12 小時一段（06–18 白天、18–06 夜間），依起始日期分組，
     取當天各時段的最高 MaxT 與最低 MinT。
  2. 只保留「白天 + 夜間」兩段都有的完整日期（第一天常只有夜間時段）。
  3. 依中央氣象署六大分區，把同一區域所有縣市的每日 MaxT / MinT 取平均。
  4. 只輸出最前面 7 個完整日期（一週），存成 weather_data.csv。
"""
import csv
import json
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

RAW_FILE = "weather_raw.json"
CSV_FILE = "weather_data.csv"
DAYS = 7

# 六大區域 → 縣市（離島：澎湖、金門、連江不列入本島六區）
REGION_COUNTIES = {
    "北部地區": ["基隆市", "臺北市", "新北市", "桃園市", "新竹市", "新竹縣"],
    "中部地區": ["苗栗縣", "臺中市", "彰化縣", "南投縣", "雲林縣"],
    "南部地區": ["嘉義市", "嘉義縣", "臺南市", "高雄市", "屏東縣"],
    "東北部地區": ["宜蘭縣"],
    "東部地區": ["花蓮縣"],
    "東南部地區": ["臺東縣"],
}
COUNTY_TO_REGION = {c: r for r, cs in REGION_COUNTIES.items() for c in cs}


def county_daily(location: dict) -> dict:
    """回傳 {date: (mint, maxt)}，只含白天+夜間兩段都齊全的日期。"""
    mint, maxt = defaultdict(list), defaultdict(list)
    for elem in location["WeatherElement"]:
        name = elem["ElementName"]
        if name not in ("最低溫度", "最高溫度"):
            continue
        for t in elem["Time"]:
            date = t["StartTime"][:10]
            value = t["ElementValue"][0]
            if name == "最低溫度":
                mint[date].append(float(value["MinTemperature"]))
            else:
                maxt[date].append(float(value["MaxTemperature"]))

    return {
        d: (min(mint[d]), max(maxt[d]))
        for d in mint
        if len(mint[d]) >= 2 and len(maxt.get(d, [])) >= 2
    }


def parse_weather():
    try:
        with open(RAW_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        sys.exit(f"Error: 找不到 {RAW_FILE}，請先執行 fetch_weather.py")

    locations = data["records"]["Locations"][0]["Location"]

    # region -> date -> [(mint, maxt), ...]
    region_days = defaultdict(lambda: defaultdict(list))
    found = set()
    for loc in locations:
        region = COUNTY_TO_REGION.get(loc["LocationName"])
        if not region:
            continue
        found.add(loc["LocationName"])
        for date, temps in county_daily(loc).items():
            region_days[region][date].append(temps)

    missing = set(COUNTY_TO_REGION) - found
    if missing:
        print(f"⚠️ JSON 中找不到這些縣市：{', '.join(sorted(missing))}")

    rows = []
    for region in REGION_COUNTIES:
        days = region_days.get(region, {})
        for date in sorted(days)[:DAYS]:
            temps = days[date]
            rows.append({
                "regionName": region,
                "dataDate": date,
                "mint": round(sum(t[0] for t in temps) / len(temps), 1),
                "maxt": round(sum(t[1] for t in temps) / len(temps), 1),
            })

    with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["regionName", "dataDate", "mint", "maxt"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"{'regionName':<8}{'dataDate':>12}{'mint':>7}{'maxt':>7}")
    for r in rows:
        print(f"{r['regionName']:<8}{r['dataDate']:>12}{r['mint']:>7}{r['maxt']:>7}")
    print(f"\n✅ 已解析 {len(rows)} 筆（6 區 × {DAYS} 天），存成 {CSV_FILE}")


if __name__ == "__main__":
    parse_weather()
