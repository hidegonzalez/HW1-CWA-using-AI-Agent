import { useEffect, useRef } from 'react';
import { colorByTemperature, getRadius } from '../colorScale';
import type { StationTemperature } from '../types';
import 'leaflet.heat'; // Will inject L.heatLayer

interface TemperatureLayerProps {
  map: any;
  stations: StationTemperature[];
  mode: 'none' | 'markers' | 'heatmap';
}

export function TemperatureLayer({ map, stations, mode }: TemperatureLayerProps) {
  const layerGroup = useRef<any>(null);
  const heatLayer = useRef<any>(null);

  useEffect(() => {
    if (!map) return;

    // Clear existing layers
    if (layerGroup.current) {
      map.removeLayer(layerGroup.current);
      layerGroup.current = null;
    }
    if (heatLayer.current) {
      map.removeLayer(heatLayer.current);
      heatLayer.current = null;
    }

    if (mode === 'none' || stations.length === 0) return;

    if (mode === 'markers') {
      layerGroup.current = window.L.layerGroup().addTo(map);
      
      stations.forEach((station) => {
        const marker = window.L.circleMarker([station.lat, station.lon], {
          radius: getRadius(station.temperature_c),
          fillColor: colorByTemperature(station.temperature_c),
          fillOpacity: 0.85,
          color: "#ffffff",
          weight: 1
        });

        marker.bindPopup(`
          <div style="padding: 4px;">
            <strong style="font-size: 16px;">${station.station_name}</strong><br/>
            <span style="color: #ccc">${station.county ?? ""} ${station.town ?? ""}</span><br/>
            <div style="margin-top: 8px; border-top: 1px solid #444; padding-top: 8px;">
              Temperature: <b>${station.temperature_c}°C</b><br/>
              Humidity: ${station.humidity_percent ?? "-"}%<br/>
              Wind: ${station.wind_speed_mps ?? "-"} m/s<br/>
            </div>
            <div style="margin-top: 8px; font-size: 11px; color: #888;">
              Time: ${new Date(station.observed_at).toLocaleString()}
            </div>
          </div>
        `);

        marker.addTo(layerGroup.current);
      });
    } else if (mode === 'heatmap') {
      // Heatmap format: [lat, lon, intensity]
      const heatData = stations.map(s => {
        // Map temperature to an intensity (e.g., 0 to 1). 
        // Assuming typical Taiwan temp ranges 10 to 40.
        let intensity = (s.temperature_c - 10) / 30;
        if (intensity < 0) intensity = 0.1;
        if (intensity > 1) intensity = 1.0;
        return [s.lat, s.lon, intensity];
      });

      // @ts-ignore
      heatLayer.current = window.L.heatLayer(heatData, {
        radius: 25,
        blur: 15,
        maxZoom: 10,
        gradient: {
          0.2: '#2b6cb0', // cold
          0.4: '#38a169', // mild
          0.6: '#ecc94b', // comfortable
          0.8: '#ed8936', // warm
          1.0: '#e53e3e'  // hot
        }
      }).addTo(map);
    }
  }, [map, stations, mode]);

  return null;
}
