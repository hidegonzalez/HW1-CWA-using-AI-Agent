import { useState, useCallback, useEffect } from 'react';
import type { StationTemperature } from './types';
import { RefreshCw } from 'lucide-react';

import { WindyMap } from './components/WindyMap';
import { TemperatureLayer } from './components/TemperatureLayer';
import { TemperatureLegend } from './components/TemperatureLegend';
import { LayerControlPanel } from './components/LayerControlPanel';
import { TimeSlider } from './components/TimeSlider';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function App() {
  const [mapObj, setMapObj] = useState<any>(null);
  const [windyStore, setWindyStore] = useState<any>(null);
  
  const [stations, setStations] = useState<StationTemperature[]>([]);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  
  const [cwaLayerMode, setCwaLayerMode] = useState<'none' | 'markers' | 'heatmap'>('markers');
  const [historyTime, setHistoryTime] = useState<string | null>(null);
  const [particlesAnim, setParticlesAnim] = useState<'on' | 'off'>('off');

  const fetchData = useCallback(async (timestamp: string | null = null) => {
    try {
      let url = `${API_BASE_URL}/api/temperature/latest`;
      if (timestamp) {
        url = `${API_BASE_URL}/api/temperature/history/${timestamp}`;
      }
      
      const res = await fetch(url);
      const data = await res.json();
      
      if (data.stations) {
        setStations(data.stations);
        setLastUpdate(data.updated_at);
      }
    } catch (e) {
      console.error("Failed to fetch CWA data", e);
    }
  }, []);

  const handleMapReady = useCallback((map: any, store: any) => {
    setMapObj(map);
    setWindyStore(store);
    store.set("particlesAnim", particlesAnim);
    fetchData(); // Initial load
  }, [fetchData, particlesAnim]);

  // Live Auto Refresh (only when historyTime is null)
  useEffect(() => {
    if (historyTime) return;
    const interval = setInterval(() => fetchData(null), 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchData, historyTime]);

  // Whenever historyTime changes, fetch the corresponding snapshot
  useEffect(() => {
    fetchData(historyTime);
  }, [historyTime, fetchData]);

  const changeWindyLayer = (overlay: string) => {
    if (windyStore) {
      windyStore.set("overlay", overlay);
    }
  };

  const toggleParticles = (isOn: boolean) => {
    const val = isOn ? 'on' : 'off';
    setParticlesAnim(val);
    if (windyStore) {
      windyStore.set("particlesAnim", val);
    }
  };

  return (
    <div className="w-full h-full relative pointer-events-none">
      <WindyMap onMapReady={handleMapReady} />
      
      <TemperatureLayer 
        map={mapObj} 
        stations={stations} 
        mode={cwaLayerMode} 
      />

      {/* Top Bar */}
      <div className="ui-layer absolute top-4 left-1/2 -translate-x-1/2 w-full max-w-2xl px-4 z-10">
        <div className="flex flex-col sm:flex-row justify-between items-center bg-black/60 backdrop-blur-md border border-white/10 rounded-xl p-4 text-white shadow-lg gap-2">
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-teal-400 bg-clip-text text-transparent text-center sm:text-left">
            CWA Temperature Broadcast
          </h1>
          <div className="flex items-center gap-4 text-sm text-gray-300">
            <span className="text-center">{historyTime ? "History mode" : "Last update"}: <br className="sm:hidden" />{lastUpdate ? new Date(lastUpdate).toLocaleTimeString() : "Loading..."}</span>
            <button 
              onClick={() => fetchData(historyTime)}
              className="p-2 hover:bg-white/10 rounded-full transition-colors shrink-0"
              title="Refresh Data"
            >
              <RefreshCw size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Controls */}
      <div className="absolute bottom-4 left-4 right-4 flex flex-col md:flex-row justify-between items-end md:items-end gap-4 z-10 pointer-events-none">
        
        {/* Left: Legend */}
        <div className="ui-layer pointer-events-auto hidden sm:block">
          <TemperatureLegend />
        </div>
        
        {/* Center: Time Slider */}
        <div className="ui-layer pointer-events-auto flex-grow w-full max-w-lg mb-2 md:mb-0">
          <TimeSlider onTimeChange={setHistoryTime} />
        </div>

        {/* Right: Layer Control */}
        <div className="ui-layer pointer-events-auto flex justify-between w-full md:w-auto">
          {/* Mobile legend button could go here, but for now we just show layers */}
          <div className="sm:hidden">
            {/* Legend is hidden on mobile to save space, but TimeSlider and LayerControl remain */}
          </div>
          <LayerControlPanel 
            cwaLayerMode={cwaLayerMode}
            setCwaLayerMode={setCwaLayerMode}
            changeWindyLayer={changeWindyLayer}
            particlesAnim={particlesAnim}
            toggleParticles={toggleParticles}
          />
        </div>

      </div>
    </div>
  );
}

export default App;
