import { useState, useEffect } from 'react';
import { Play, Pause } from 'lucide-react';

interface TimeSliderProps {
  onTimeChange: (timestamp: string | null) => void;
}

export function TimeSlider({ onTimeChange }: TimeSliderProps) {
  const [historyDates, setHistoryDates] = useState<string[]>([]);
  const [currentIndex, setCurrentIndex] = useState(-1);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    // Fetch available history timestamps
    const fetchHistory = async () => {
      try {
        const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
        const res = await fetch(`${API_BASE_URL}/api/temperature/history`);
        const data = await res.json();
        setHistoryDates(data);
      } catch (e) {
        console.error("Failed to fetch history dates", e);
      }
    };
    fetchHistory();
    // Refresh history list every 5 minutes
    const interval = setInterval(fetchHistory, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (currentIndex >= 0 && currentIndex < historyDates.length) {
      onTimeChange(historyDates[currentIndex]);
    } else {
      onTimeChange(null); // null means "live data"
    }
  }, [currentIndex, historyDates, onTimeChange]);

  useEffect(() => {
    let interval: any;
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentIndex(prev => {
          if (prev >= historyDates.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isPlaying, historyDates.length]);

  if (historyDates.length === 0) {
    return (
      <div className="bg-black/60 backdrop-blur-md border border-white/10 rounded-xl p-4 text-white shadow-lg flex items-center justify-center text-sm text-gray-400">
        Waiting for historical data...
      </div>
    );
  }

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCurrentIndex(parseInt(e.target.value, 10));
  };

  const isLive = currentIndex === -1;
  const displayTime = isLive 
    ? "Live (Latest)" 
    : new Date(historyDates[currentIndex]).toLocaleString();

  return (
    <div className="bg-black/60 backdrop-blur-md border border-white/10 rounded-xl p-4 text-white shadow-lg flex flex-col gap-3">
      <div className="flex justify-between items-center">
        <span className="font-semibold text-sm">Time Slider</span>
        <span className="text-sm text-blue-300 font-bold">{displayTime}</span>
      </div>
      <div className="flex items-center gap-4">
        <button 
          onClick={() => setIsPlaying(!isPlaying)}
          disabled={isLive || currentIndex >= historyDates.length - 1}
          className="p-2 rounded-full hover:bg-white/10 transition-colors disabled:opacity-50"
        >
          {isPlaying ? <Pause size={20} /> : <Play size={20} />}
        </button>
        <input 
          type="range" 
          min="-1" 
          max={historyDates.length - 1} 
          value={currentIndex} 
          onChange={handleSliderChange}
          className="flex-grow h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"
        />
        <button 
          onClick={() => {
            setCurrentIndex(-1);
            setIsPlaying(false);
          }}
          className={`text-xs px-2 py-1 rounded ${isLive ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'}`}
        >
          Live
        </button>
      </div>
    </div>
  );
}
