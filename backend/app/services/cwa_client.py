import httpx
from ..config import settings
import ssl

INVALID_VALUES = {"", "X", "NA", "null", None, "-99", "-999", "-99.0", "-99.00"}

def parse_float(value):
    if str(value).strip() in INVALID_VALUES:
        return None
    try:
        f = float(value)
        if f <= -90.0:
            return None
        return f
    except (ValueError, TypeError):
        return None

async def fetch_cwa_observations():
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization={settings.CWA_API_KEY}&format=JSON"
    
    # We must disable strict X509 checks for CWA API to work on python 3.14
    ctx = ssl.create_default_context()
    ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
    
    async with httpx.AsyncClient(verify=ctx) as client:
        response = await client.get(url, timeout=30.0)
        response.raise_for_status()
        return response.json()
