from fastapi import APIRouter, HTTPException
from ..services.temperature_service import get_latest
from ..schemas.temperature import LatestTemperatureResponse
import datetime

router = APIRouter(prefix="/api/temperature", tags=["temperature"])

@router.get("/latest", response_model=LatestTemperatureResponse)
async def get_latest_temperature():
    try:
        stations, status, latest_time = await get_latest()
        return LatestTemperatureResponse(
            source="CWA",
            updated_at=latest_time or datetime.datetime.now().isoformat(),
            count=len(stations),
            stations=stations
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/history")
async def get_history_timestamps():
    from ..services.db_service import get_history_snapshots
    try:
        return get_history_snapshots()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{timestamp}", response_model=LatestTemperatureResponse)
async def get_history_snapshot(timestamp: str):
    from ..services.db_service import get_snapshot
    try:
        data = get_snapshot(timestamp)
        if not data:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        return LatestTemperatureResponse(
            source="CWA (History)",
            updated_at=timestamp,
            count=len(data),
            stations=data
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/geojson")
async def get_temperature_geojson():
    try:
        stations, status, latest_time = await get_latest()
        
        features = []
        for s in stations:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [s.lon, s.lat]
                },
                "properties": {
                    "station_id": s.station_id,
                    "station_name": s.station_name,
                    "temperature_c": s.temperature_c,
                    "county": s.county,
                    "town": s.town,
                    "humidity_percent": s.humidity_percent,
                    "wind_speed_mps": s.wind_speed_mps,
                    "observed_at": s.observed_at.isoformat()
                }
            })
            
        return {
            "type": "FeatureCollection",
            "features": features
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
