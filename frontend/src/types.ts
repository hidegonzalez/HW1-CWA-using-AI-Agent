export interface StationTemperature {
    station_id: string;
    station_name: string;
    county: string | null;
    town: string | null;
    lat: number;
    lon: number;
    altitude_m: number | null;
    observed_at: string;
    temperature_c: number;
    humidity_percent: number | null;
    pressure_hpa: number | null;
    wind_speed_mps: number | null;
    wind_direction_deg: number | null;
    precipitation_mm: number | null;
    weather: string | null;
}

export interface LatestTemperatureResponse {
    source: string;
    updated_at: string;
    count: number;
    stations: StationTemperature[];
}
