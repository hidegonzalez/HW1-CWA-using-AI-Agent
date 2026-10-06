"""Step 1：取得 CWA API 資料（作業圖卡 1）

依照作業規格：
  1. 使用 requests 呼叫 CWA API（授權碼放在 headers 的 Authorization）
  2. 使用 json.dumps 觀察回傳的 JSON 資料
  3. 確認資料取得成功，並存成 weather_raw.json 給 parse_weather.py 使用

資料集說明：
  作業指定的 F-A0010-001（六大區域一週預報）目前在 CWA 開放平台已回傳 404，
  因此先嘗試 F-A0010-001，失敗時自動改用 F-D0047-091（臺灣各縣市一週預報），
  再由 parse_weather.py 把 22 縣市彙整回作業要求的 6 大區域。
"""
import json
import os
import ssl
import sys

import requests
from requests.adapters import HTTPAdapter
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
API_KEY = os.getenv("CWA_API_KEY")
if not API_KEY:
    sys.exit("Error: 請在 .env 設定 CWA_API_KEY（使用自己的金鑰）")

BASE_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/"
PRIMARY_DATASET = "F-A0010-001"   # 作業指定（目前已停止提供）
FALLBACK_DATASET = "F-D0047-091"  # 臺灣各縣市一週天氣預報
RAW_FILE = "weather_raw.json"


class CWAAdapter(HTTPAdapter):
    """CWA 憑證缺少 Subject Key Identifier，Python 3.13+ 的嚴格檢查會拒絕。
    這裡只關閉 VERIFY_X509_STRICT，憑證驗證本身仍然開啟。"""

    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
        kwargs["ssl_context"] = ctx
        return super().init_poolmanager(*args, **kwargs)


def fetch(dataset_id: str, session: requests.Session) -> requests.Response:
    url = f"{BASE_URL}{dataset_id}"
    headers = {"Authorization": API_KEY}
    return session.get(url, headers=headers, params={"format": "JSON"}, timeout=30)


def main():
    session = requests.Session()
    session.mount("https://", CWAAdapter())

    print(f"呼叫 CWA API：{PRIMARY_DATASET} ...")
    resp = fetch(PRIMARY_DATASET, session)
    dataset_id = PRIMARY_DATASET
    if resp.status_code == 404:
        print(f"  {PRIMARY_DATASET} 回傳 404（資料集已停止提供），改用 {FALLBACK_DATASET}")
        resp = fetch(FALLBACK_DATASET, session)
        dataset_id = FALLBACK_DATASET

    resp.raise_for_status()
    data = resp.json()

    if data.get("success") != "true":
        sys.exit(f"API 回傳失敗：{json.dumps(data, ensure_ascii=False)[:500]}")

    # 觀察 JSON 結構：完整內容約 1 MB，終端機只顯示第一個地點的前段
    preview = {
        "success": data["success"],
        "result": data.get("result", {}).get("resource_id"),
        "records": {
            "Locations": [{
                **{k: v for k, v in data["records"]["Locations"][0].items() if k != "Location"},
                "Location": data["records"]["Locations"][0]["Location"][:1],
            }]
        },
    }
    text = json.dumps(preview, indent=2, ensure_ascii=False)
    print(text[:3000] + ("\n... (以下省略，完整內容見 weather_raw.json)" if len(text) > 3000 else ""))

    with open(RAW_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    n_loc = len(data["records"]["Locations"][0]["Location"])
    print(f"\n✅ 資料取得成功：{dataset_id}，共 {n_loc} 個地點，已存成 {RAW_FILE}")


if __name__ == "__main__":
    main()
