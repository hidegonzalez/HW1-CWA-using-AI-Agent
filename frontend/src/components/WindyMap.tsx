import { useEffect, useRef } from 'react';

interface WindyMapProps {
  onMapReady: (map: any, store: any) => void;
}

export function WindyMap({ onMapReady }: WindyMapProps) {
  const initialized = useRef(false);

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    const searchParams = new URLSearchParams(window.location.search);
    const urlLat = searchParams.get('lat');
    const urlLon = searchParams.get('lon');
    const urlZoom = searchParams.get('zoom');

    const urlTime = searchParams.get('time');

    const options = {
      key: import.meta.env.VITE_WINDY_API_KEY,
      lat: urlLat ? parseFloat(urlLat) : 23.7,
      lon: urlLon ? parseFloat(urlLon) : 121.0,
      zoom: urlZoom ? parseInt(urlZoom, 10) : 7,
      overlay: "wind",
      labels: false, // Attempt to disable labels
    };

    window.windyInit(options, (windyAPI) => {
      const { map, store } = windyAPI;
      store.set("overlay", "wind");
      
      // Attempt to hide Windy city labels
      if (windyAPI.labelsLayer) {
        map.removeLayer(windyAPI.labelsLayer);
      }

      // Sync time if requested
      if (urlTime && urlTime !== 'None' && urlTime !== 'null' && urlTime !== 'undefined') {
        const parsed = new Date(urlTime.includes('T') ? urlTime : `${urlTime}T12:00:00+08:00`).getTime();
        if (!isNaN(parsed)) {
          store.set('timestamp', parsed);
        }
      }

      onMapReady(map, store);
    });
  }, [onMapReady]);

  // The actual Windy map is rendered into #windy div in index.html outside of React root.
  // This component just orchestrates the initialization.
  return null;
}
