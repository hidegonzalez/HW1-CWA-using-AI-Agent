from datetime import datetime, timezone
from ..schemas.temperature import StationTemperature
from .cwa_client import fetch_cwa_observations, parse_float
import time

_cache = {
    "data": None,
    "updated_at": 0,
    "latest_cwa_time": None
}

async def get_latest():
    from ..config import settings
    now = time.time()
    
    # Return cache if valid
    if _cache["data"] and (now - _cache["updated_at"] < settings.CACHE_TTL_SECONDS):
        return _cache["data"], "fresh", _cache["latest_cwa_time"]
        
    try:
        raw_data = await fetch_cwa_observations()
        stations = parse_cwa_data(raw_data)
        
        if stations:
            _cache["data"] = stations
            _cache["updated_at"] = now
            latest_time = stations[0].observed_at.isoformat()
            _cache["latest_cwa_time"] = latest_time
            
            # Phase 4: Save to database for historical playback
            from .db_service import save_snapshot
            save_snapshot(latest_time, stations)
            
            return stations, "fresh", _cache["latest_cwa_time"]
    except Exception as e:
        print(f"Failed to fetch CWA data: {e}")
        
    # Return stale cache if available
    if _cache["data"]:
        return _cache["data"], "stale", _cache["latest_cwa_time"]
        
    raise Exception("CWA fetch failed and no cache available")

def parse_cwa_data(raw_data):
    records = raw_data.get("records", {})
    station_list = records.get("Station", [])
    
    valid_stations = []
    
    for s in station_list:
        try:
            # Coordinates (prefer WGS84)
            geo = s.get("GeoInfo", {})
            coords_list = geo.get("Coordinates", [])
            lat, lon = None, None
            for c in coords_list:
                if c.get("CoordinateName") == "WGS84":
                    lat = parse_float(c.get("StationLatitude"))
                    lon = parse_float(c.get("StationLongitude"))
                    break
            if lat is None or lon is None:
                if coords_list:
                    lat = parse_float(coords_list[0].get("StationLatitude"))
                    lon = parse_float(coords_list[0].get("StationLongitude"))
            
            # Weather Elements
            we = s.get("WeatherElement", {})
            temp = parse_float(we.get("AirTemperature"))
            
            if lat is None or lon is None or temp is None:
                continue
                
            if temp < -20 or temp > 50:
                continue
                
            now_we = we.get("Now", {})
            
            # Observation Time
            obs_time_str = s.get("ObsTime", {}).get("DateTime")
            try:
                obs_time = datetime.fromisoformat(obs_time_str)
            except:
                obs_time = datetime.now(timezone.utc)
                
            station = StationTemperature(
                station_id=s.get("StationId"),
                station_name=s.get("StationName"),
                county=geo.get("CountyName"),
                town=geo.get("TownName"),
                lat=lat,
                lon=lon,
                altitude_m=parse_float(geo.get("StationAltitude")),
                observed_at=obs_time,
                temperature_c=temp,
                humidity_percent=parse_float(we.get("RelativeHumidity")),
                pressure_hpa=parse_float(we.get("AirPressure")),
                wind_speed_mps=parse_float(we.get("WindSpeed")),
                wind_direction_deg=parse_float(we.get("WindDirection")),
                precipitation_mm=parse_float(now_we.get("Precipitation")),
                weather=we.get("Weather")
            )
            valid_stations.append(station)
        except Exception as e:
            # skip invalid stations gracefully
            pass
            
    return valid_stations
