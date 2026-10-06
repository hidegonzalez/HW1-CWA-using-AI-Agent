export function TemperatureLegend() {
  return (
    <div className="bg-black/60 backdrop-blur-md border border-white/10 rounded-xl p-4 text-white shadow-lg flex flex-col gap-2">
      <div className="font-semibold text-sm mb-1 text-gray-300">Temperature</div>
      <div className="flex items-center gap-2 text-sm"><span className="w-3 h-3 rounded-full bg-[#2b6cb0]"></span> &lt; 10°C (cold)</div>
      <div className="flex items-center gap-2 text-sm"><span className="w-3 h-3 rounded-full bg-[#3182ce]"></span> 10–15°C (cool)</div>
      <div className="flex items-center gap-2 text-sm"><span className="w-3 h-3 rounded-full bg-[#38a169]"></span> 15–20°C (mild)</div>
      <div className="flex items-center gap-2 text-sm"><span className="w-3 h-3 rounded-full bg-[#ecc94b]"></span> 20–25°C (comfortable)</div>
      <div className="flex items-center gap-2 text-sm"><span className="w-3 h-3 rounded-full bg-[#ed8936]"></span> 25–30°C (warm)</div>
      <div className="flex items-center gap-2 text-sm"><span className="w-3 h-3 rounded-full bg-[#e53e3e]"></span> 30–35°C (hot)</div>
      <div className="flex items-center gap-2 text-sm"><span className="w-3 h-3 rounded-full bg-[#9b2c2c]"></span> &gt; 35°C (very hot)</div>
    </div>
  );
}
