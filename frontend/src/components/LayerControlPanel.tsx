import { Layers } from 'lucide-react';
import { useState } from 'react';

interface LayerControlPanelProps {
  cwaLayerMode: 'none' | 'markers' | 'heatmap';
  setCwaLayerMode: (mode: 'none' | 'markers' | 'heatmap') => void;
  changeWindyLayer: (overlay: string) => void;
  particlesAnim: 'on' | 'off';
  toggleParticles: (isOn: boolean) => void;
}

export function LayerControlPanel({ cwaLayerMode, setCwaLayerMode, changeWindyLayer, particlesAnim, toggleParticles }: LayerControlPanelProps) {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">
      <button 
        onClick={() => setOpen(!open)}
        className="bg-black/60 backdrop-blur-md border border-white/10 rounded-full p-4 text-white shadow-lg hover:bg-black/80 transition-all"
      >
        <Layers size={24} />
      </button>

      {open && (
        <div className="absolute bottom-full right-0 mb-4 bg-black/80 backdrop-blur-md border border-white/10 rounded-xl p-4 text-white shadow-xl min-w-[200px] w-64 max-h-[60vh] overflow-y-auto flex flex-col gap-3 z-50">
          <h3 className="font-semibold text-sm text-gray-400 border-b border-white/10 pb-2">CWA Overlay</h3>
          <label className="flex items-center gap-2 cursor-pointer text-sm hover:text-blue-300">
            <input 
              type="radio" 
              checked={cwaLayerMode === 'none'} 
              onChange={() => setCwaLayerMode('none')} 
              className="rounded" 
            />
            Hidden
          </label>
          <label className="flex items-center gap-2 cursor-pointer text-sm hover:text-blue-300">
            <input 
              type="radio" 
              checked={cwaLayerMode === 'markers'} 
              onChange={() => setCwaLayerMode('markers')} 
              className="rounded" 
            />
            Station Markers
          </label>
          <label className="flex items-center gap-2 cursor-pointer text-sm hover:text-blue-300">
            <input 
              type="radio" 
              checked={cwaLayerMode === 'heatmap'} 
              onChange={() => setCwaLayerMode('heatmap')} 
              className="rounded" 
            />
            Heatmap
          </label>

          <h3 className="font-semibold text-sm text-gray-400 border-b border-white/10 pb-2 mt-2">Windy Background</h3>
          <label className="flex items-center gap-2 cursor-pointer text-sm hover:text-blue-300 pb-1 border-b border-white/10">
            <input 
              type="checkbox" 
              checked={particlesAnim === 'on'} 
              onChange={(e) => toggleParticles(e.target.checked)} 
              className="rounded" 
            />
            Wind Particles Animation
          </label>
          
          {["wind", "temp", "rain", "clouds"].map(layer => (
            <button 
              key={layer}
              onClick={() => {
                changeWindyLayer(layer);
                setOpen(false);
              }}
              className="text-left text-sm hover:text-blue-300 capitalize py-1"
            >
              • {layer}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
