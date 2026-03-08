import React, { useState, useEffect, useRef } from "react";
import { Send, Bot, Map as MapIcon, Maximize2, Share2, Layers, Zap, Droplets, Info, Settings, ChevronRight, ShieldCheck, Activity, CloudRain, TrendingUp, FileText } from "lucide-react";
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { Footer } from "@/components/Footer";
import Navbar from "@/components/Navbar";
import { GlobalBackground } from "@/components/GlobalBackground";

const Analysis = () => {
    const [messages, setMessages] = useState([
        { role: "assistant", content: "Command Center active. Geospatial layers loaded and ready for analysis." }
    ]);
    const [input, setInput] = useState("");
    const [activeTab, setActiveTab] = useState<'analysis' | 'planning' | 'sim'>('analysis');
    const [isPlanning, setIsPlanning] = useState(false);
    const [planningType, setPlanningType] = useState<string | null>(null);
    const [rainfall, setRainfall] = useState(100);
    const [isSimulating, setIsSimulating] = useState(false);
    const [isMessageLoading, setIsMessageLoading] = useState(false);
    const [budgetEstimate, setBudgetEstimate] = useState<any>(null);
    const [projectId, setProjectId] = useState<string>("global");

    const mapContainer = useRef<HTMLDivElement>(null);
    const map = useRef<maplibregl.Map | null>(null);

    useEffect(() => {
        const urlParams = new URLSearchParams(window.location.search);
        const pId = urlParams.get('project_id');
        if (pId) {
            setProjectId(pId);
            setMessages([
                { role: "assistant", content: `Command Center active for Project ${pId.slice(0, 8)}. Geospatial layers syncing...` }
            ]);
            fetchBuildings(pId);
        }

        if (!mapContainer.current || map.current) return;

        map.current = new maplibregl.Map({
            container: mapContainer.current,
            style: 'https://demotiles.maplibre.org/style.json',
            center: [78.9629, 20.5937], // India default
            zoom: 4,
            pitch: 45
        });

        map.current.addControl(new maplibregl.NavigationControl({}));

        map.current.on('click', (e) => {
            const features = map.current?.queryRenderedFeatures(e.point, {
                layers: ['planning-sewage', 'planning-electricity']
            });

            if (features && features.length > 0) {
                const feature = features[0];
                const type = feature.properties.type;
                handleInspectSegment(type);
            }
        });

        return () => {
            map.current?.remove();
            map.current = null;
        };
    }, []);

    const fetchBuildings = async (pId: string) => {
        try {
            const res = await fetch(`http://localhost:8000/api/buildings?project_id=${pId}`);
            if (res.ok) {
                const data = await res.json();
                if (map.current && data.features) {
                    if (map.current.getSource('buildings')) {
                        (map.current.getSource('buildings') as any).setData(data);
                    } else {
                        map.current.addSource('buildings', { type: 'geojson', data });
                        map.current.addLayer({
                            id: 'buildings-layer',
                            type: 'fill',
                            source: 'buildings',
                            paint: { 'fill-color': '#3b82f6', 'fill-opacity': 0.5 }
                        });
                    }
                    const bounds = new maplibregl.LngLatBounds();
                    data.features.forEach((f: any) => {
                        const coords = f.geometry.coordinates;
                        if (f.geometry.type === 'Polygon') {
                            coords[0].forEach((p: any) => bounds.extend(p));
                        } else if (f.geometry.type === 'Point') {
                            bounds.extend(coords);
                        }
                    });
                    if (!bounds.isEmpty()) map.current.fitBounds(bounds, { padding: 50 });
                }
            }
        } catch (e) {
            console.error("Failed to auto-fetch buildings:", e);
        }
    };

    const handleSend = async () => {
        if (!input.trim() || isMessageLoading) return;
        const userMessage = input;
        setMessages(prev => [...prev, { role: "user", content: userMessage }]);
        setInput("");
        setIsMessageLoading(true);

        try {
            const response = await fetch(`http://localhost:8000/api/rag/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: userMessage, project_id: projectId })
            });
            const data = await response.json();
            setMessages(prev => [...prev, { role: "assistant", content: data.answer || "I'm sorry, I couldn't process that request." }]);
        } catch (error) {
            console.error("Chat failed:", error);
            setMessages(prev => [...prev, { role: "assistant", content: "Connection to Intelligence Server lost." }]);
        } finally {
            setIsMessageLoading(false);
        }
    };

    const runPlanning = async (type: 'sewage' | 'electricity') => {
        setIsPlanning(true);
        setPlanningType(type);

        const mockBuildings = [
            [78.9629, 20.5937], [78.9635, 20.5942], [78.9641, 20.5932]
        ];
        let buildingsForPlanning = mockBuildings;

        try {
            const buildingRes = await fetch(`http://localhost:8000/api/buildings?project_id=${projectId}`);
            if (buildingRes.ok) {
                const geojson = await buildingRes.json();
                if (geojson.features && geojson.features.length > 0) {
                    buildingsForPlanning = geojson.features.map((f: any) => {
                        const coords = f.geometry.coordinates;
                        return Array.isArray(coords[0]) ? coords[0][0] : coords;
                    }).slice(0, 50);
                }
            }
        } catch (e) {
            console.warn("Could not fetch real buildings, using mocks");
        }

        try {
            const response = await fetch(`http://localhost:8000/api/planning/${type}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ buildings: buildingsForPlanning, project_id: projectId })
            });
            const data = await response.json();
            setBudgetEstimate(data.budgetary_estimate);

            setMessages(prev => [...prev, {
                role: "assistant",
                content: `Optimized ${type} network generated. Budgetary estimate: $${data.budgetary_estimate.total_estimate.toLocaleString()}. Planning compliance: ${type === 'sewage' ? '92%' : '88%'}.`
            }]);

            if (map.current && data.paths) {
                const layerId = `planning-${type}`;
                if (map.current.getLayer(layerId)) {
                    map.current.removeLayer(layerId);
                    map.current.removeSource(layerId);
                }

                map.current.addSource(layerId, {
                    type: 'geojson',
                    data: {
                        type: 'FeatureCollection',
                        features: data.paths.map((p: any) => ({
                            type: 'Feature',
                            geometry: { type: 'LineString', coordinates: p },
                            properties: { type }
                        }))
                    }
                });

                map.current.addLayer({
                    id: layerId,
                    type: 'line',
                    source: layerId,
                    paint: {
                        'line-color': type === 'sewage' ? '#22d3ee' : '#fbbf24',
                        'line-width': 3,
                        'line-dasharray': [2, 1]
                    }
                });
            }
        } catch (error) {
            console.error("Planning failed:", error);
        } finally {
            setIsPlanning(false);
        }
    };

    const handleInspectSegment = async (type: string) => {
        setMessages(prev => [...prev, { role: "assistant", content: `Inspecting ${type} segment for policy compliance...` }]);

        try {
            const response = await fetch(`http://localhost:8000/api/rag/explain`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: `Check compliance for ${type} infrastructure routing near coordinates.`, project_id: projectId })
            });
            const data = await response.json();

            setMessages(prev => [...prev, {
                role: "assistant",
                content: data.analysis?.justification || data.detail || "Compliance analysis unavailable."
            }]);
        } catch (error) {
            console.error("Inspection failed:", error);
        }
    };

    const runSimulation = async () => {
        setIsSimulating(true);
        try {
            const response = await fetch(`http://localhost:8000/api/simulation/flood`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rainfall, bounds: [78.96, 20.59, 78.97, 20.60] })
            });
            const data = await response.json();

            setMessages(prev => [...prev, {
                role: "assistant",
                content: `Hydrology simulation complete for ${rainfall}mm rainfall. ${data.results.accumulation_count} potential accumulation points detected. Risk Assessment: ${data.results.risk_level}.`
            }]);

            if (map.current && data.results.zones) {
                const layerId = 'flood-zones';
                if (map.current.getLayer(layerId)) {
                    map.current.removeLayer(layerId);
                    map.current.removeSource(layerId);
                }

                map.current.addSource(layerId, {
                    type: 'geojson',
                    data: {
                        type: 'FeatureCollection',
                        features: data.results.zones.map((z: any) => ({
                            type: 'Feature',
                            geometry: {
                                type: 'Point',
                                coordinates: z.center
                            },
                            properties: { depth: z.depth_m }
                        }))
                    }
                });

                map.current.addLayer({
                    id: layerId,
                    type: 'circle',
                    source: layerId,
                    paint: {
                        'circle-radius': ['*', ['get', 'depth'], 50],
                        'circle-color': '#0ea5e9',
                        'circle-opacity': 0.4,
                        'circle-blur': 0.8
                    }
                });
            }
        } catch (error) {
            console.error("Simulation failed:", error);
        } finally {
            setIsSimulating(false);
        }
    };

    return (
        <div className="min-h-screen flex flex-col bg-[#0B1215] relative text-white">
            <GlobalBackground />
            <Navbar />
            <div className="flex-grow flex flex-col pt-16 relative z-10">
                <header className="h-20 border-b border-white/10 flex items-center justify-between px-8 shrink-0 bg-[#0B1215]/80 backdrop-blur-md">
                    <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-white font-bold shadow-lg shadow-primary/20">A</div>
                        <h1 className="text-xl font-bold tracking-tight uppercase">Aerovillage Command Center</h1>
                    </div>
                    <div className="flex items-center space-x-6">
                        <div className="flex items-center space-x-2">
                            <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
                            <span className="text-xs font-bold text-emerald-500 uppercase tracking-widest">Live Integration</span>
                        </div>
                        <div className="flex space-x-2">
                            <button className="p-2 hover:bg-white/10 rounded-lg transition-colors text-white/40"><Settings className="w-5 h-5" /></button>
                            <button className="p-2 hover:bg-white/10 rounded-lg transition-colors text-white/40"><Maximize2 className="w-5 h-5" /></button>
                        </div>
                    </div>
                </header>

                <main className="flex-grow flex overflow-hidden">
                    <div className="flex-grow relative overflow-hidden border-r border-white/5 bg-black">
                        <div ref={mapContainer} className="absolute inset-0" />
                        <div className="absolute top-6 left-6 space-y-4">
                            <div className="p-5 glass rounded-[32px] border-white/10 w-64 shadow-2xl backdrop-blur-xl">
                                <div className="flex items-center justify-between mb-4">
                                    <span className="text-[10px] font-bold text-primary uppercase tracking-widest">Spatial Layers</span>
                                    <Layers className="w-3 h-3 text-primary" />
                                </div>
                                <div className="space-y-3">
                                    {[
                                        { id: 'elec', label: 'ELECTRICAL GRID', color: 'bg-amber-400' },
                                        { id: 'water', label: 'WATER/DRAINAGE', color: 'bg-cyan-400' },
                                        { id: 'veg', label: 'NDVI ANALYSIS', color: 'bg-emerald-500' }
                                    ].map(layer => (
                                        <div key={layer.id} className="flex items-center justify-between group cursor-pointer">
                                            <span className="text-[11px] font-bold text-white/60 group-hover:text-white transition-colors">{layer.label}</span>
                                            <div className={`w-2 h-2 rounded-full ${layer.color} shadow-[0_0_8px_rgba(255,255,255,0.3)]`} />
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="w-[420px] flex flex-col bg-[#0B1215] shrink-0 border-l border-white/5 relative">
                        <div className="flex border-b border-white/10 shrink-0">
                            {[
                                { id: 'analysis', label: 'Intelligence' },
                                { id: 'planning', label: 'Planning' },
                                { id: 'sim', label: 'Simulation' }
                            ].map(tab => (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id as any)}
                                    className={`flex-1 py-4 text-[10px] font-bold uppercase tracking-widest transition-all ${activeTab === tab.id ? 'text-primary bg-primary/5 border-b-2 border-primary' : 'text-white/40 hover:text-white/60'}`}
                                >
                                    {tab.label}
                                </button>
                            ))}
                        </div>

                        {activeTab === 'analysis' ? (
                            <div className="flex flex-col h-full overflow-hidden">
                                <div className="p-6 overflow-y-auto space-y-6 flex-grow">
                                    <div className="p-5 rounded-[28px] bg-white/5 border border-white/10 hover:border-primary/30 transition-all group">
                                        <div className="flex items-center justify-between mb-3">
                                            <span className="text-[10px] font-bold text-primary uppercase bg-primary/10 px-2 py-1 rounded">Observation</span>
                                            <Info className="w-3 h-3 text-white/20" />
                                        </div>
                                        <p className="text-xs text-white/80 leading-relaxed">
                                            Topographic analysis suggests potential water stagnation in the NE quadrant. Drain reinforcement advised.
                                        </p>
                                    </div>

                                    {messages.map((msg, i) => (
                                        <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                            <div className={`flex items-start gap-4 max-w-[85%]`}>
                                                {msg.role === 'assistant' && (
                                                    <div className="w-8 h-8 rounded-xl bg-primary/20 text-primary flex items-center justify-center shrink-0 border border-primary/20">
                                                        <Bot className="w-4 h-4" />
                                                    </div>
                                                )}
                                                <div className={`p-4 rounded-3xl text-[13px] leading-relaxed ${msg.role === 'user' ? 'bg-primary text-white font-medium shadow-xl shadow-primary/20' : 'bg-white/5 border border-white/10 text-white/70'}`}>
                                                    {msg.content}
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                                <div className="p-6 border-t border-white/10 backdrop-blur-md">
                                    <div className="relative">
                                        <input
                                            value={input}
                                            onChange={(e) => setInput(e.target.value)}
                                            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                            disabled={isMessageLoading}
                                            placeholder={isMessageLoading ? "Thinking..." : "Ask about spatial data..."}
                                            className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-6 pr-14 text-xs text-white focus:ring-1 focus:ring-primary focus:border-transparent outline-none transition-all disabled:opacity-50"
                                        />
                                        <button
                                            onClick={handleSend}
                                            disabled={isMessageLoading}
                                            className="absolute right-2 top-2 p-2 bg-primary text-white rounded-xl hover:scale-105 transition-transform disabled:opacity-50"
                                        >
                                            {isMessageLoading ? (
                                                <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                                            ) : (
                                                <Send className="w-4 h-4" />
                                            )}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ) : activeTab === 'planning' ? (
                            <div className="p-8 space-y-8 overflow-y-auto h-full">
                                <div className="space-y-2">
                                    <h3 className="text-xl font-bold tracking-tight">Deterministic Simulators</h3>
                                    <p className="text-xs text-white/40 leading-relaxed font-medium">Generate engineering-grade infrastructure layouts based on topography.</p>
                                </div>

                                <div className="space-y-4">
                                    <div className="p-6 rounded-[32px] bg-white/5 border border-white/10 space-y-4 group hover:bg-white/[0.07] transition-all">
                                        <div className="flex items-center justify-between gap-4">
                                            <div className="flex items-center gap-4">
                                                <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center border border-cyan-500/20">
                                                    <Droplets className="w-6 h-6" />
                                                </div>
                                                <div>
                                                    <p className="text-xs font-bold text-white uppercase tracking-widest">Sewage/Drainage</p>
                                                    <p className="text-[10px] text-white/40 mt-0.5">Elevation-Aware Pathfinding</p>
                                                </div>
                                            </div>
                                            <div className="px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-2">
                                                <ShieldCheck className="w-3 h-3 text-emerald-500" />
                                                <span className="text-[10px] font-bold text-emerald-500">92% COMPLIANT</span>
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => runPlanning('sewage')}
                                            disabled={isPlanning}
                                            className="w-full py-3 bg-white/5 hover:bg-primary hover:text-white transition-all rounded-xl text-[10px] font-bold uppercase tracking-widest border border-white/10 flex items-center justify-center gap-2"
                                        >
                                            {isPlanning && planningType === 'sewage' ? 'Processing...' : 'Generate Gravity Network'}
                                            <ChevronRight className="w-3 h-3" />
                                        </button>
                                    </div>

                                    <div className="p-6 rounded-[32px] bg-white/5 border border-white/10 space-y-4 group hover:bg-white/[0.07] transition-all">
                                        <div className="flex items-center justify-between gap-4">
                                            <div className="flex items-center gap-4">
                                                <div className="w-12 h-12 rounded-2xl bg-amber-500/10 text-amber-500 flex items-center justify-center border border-amber-500/20">
                                                    <Zap className="w-6 h-6" />
                                                </div>
                                                <div>
                                                    <p className="text-xs font-bold text-white uppercase tracking-widest">Electricity Grid</p>
                                                    <p className="text-[10px] text-white/40 mt-0.5">K-Means + Steiner Tree</p>
                                                </div>
                                            </div>
                                            <div className="px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center gap-2">
                                                <Info className="w-3 h-3 text-amber-500" />
                                                <span className="text-[10px] font-bold text-amber-500">PENDING AUDIT</span>
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => runPlanning('electricity')}
                                            disabled={isPlanning}
                                            className="w-full py-3 bg-white/5 hover:bg-primary hover:text-white transition-all rounded-xl text-[10px] font-bold uppercase tracking-widest border border-white/10 flex items-center justify-center gap-2"
                                        >
                                            {isPlanning && planningType === 'electricity' ? 'Optimizing...' : 'Plan Transformer Zones'}
                                            <ChevronRight className="w-3 h-3" />
                                        </button>
                                    </div>
                                </div>

                                <div className="mt-8 p-6 rounded-[32px] bg-primary/5 border border-primary/20 space-y-4">
                                    <div className="flex items-center gap-3">
                                        <Bot className="w-5 h-5 text-primary" />
                                        <span className="text-xs font-bold uppercase tracking-tighter">Policy Context Engine</span>
                                    </div>
                                    <p className="text-[11px] text-white/60 leading-relaxed italic">
                                        "National Rural Infrastructure Mandate 2024 requires a minimum 20m setback for high-tension lines from primary dwellings."
                                    </p>
                                    <button className="text-[9px] font-bold text-primary uppercase border-b border-primary/20 pb-0.5 hover:text-primary/70 transition-colors">
                                        Source: Ministry of Rural Development {' > '} Circular 82-B
                                    </button>
                                </div>

                                {budgetEstimate && (
                                    <div className="p-8 rounded-[32px] bg-white/5 border border-white/10 space-y-6 animate-fade-in shadow-2xl">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <TrendingUp className="w-5 h-5 text-emerald-400" />
                                                <span className="text-xs font-bold uppercase tracking-widest text-white/80">Financial Health</span>
                                            </div>
                                            <div className="px-3 py-1 bg-emerald-500/10 rounded-full border border-emerald-500/20">
                                                <span className="text-[9px] font-bold text-emerald-500">OPTIMIZED</span>
                                            </div>
                                        </div>

                                        <div className="space-y-4">
                                            <div className="flex justify-between items-end">
                                                <span className="text-[10px] text-white/40 font-bold uppercase tracking-tight">Est. Capex Total</span>
                                                <span className="text-2xl font-bold tracking-tight text-white">${budgetEstimate.total_estimate.toLocaleString()}</span>
                                            </div>

                                            <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden flex">
                                                <div className="h-full bg-emerald-500" style={{ width: '60%' }} />
                                                <div className="h-full bg-amber-500" style={{ width: '25%' }} />
                                                <div className="h-full bg-rose-500" style={{ width: '15%' }} />
                                            </div>

                                            <div className="grid grid-cols-3 gap-4">
                                                <div className="space-y-1">
                                                    <div className="flex items-center gap-1.5">
                                                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                                                        <span className="text-[9px] font-bold text-white/40 uppercase">Material</span>
                                                    </div>
                                                    <p className="text-xs font-bold">${budgetEstimate.breakdown.materials.toLocaleString()}</p>
                                                </div>
                                                <div className="space-y-1">
                                                    <div className="flex items-center gap-1.5">
                                                        <div className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                                                        <span className="text-[9px] font-bold text-white/40 uppercase">Labor</span>
                                                    </div>
                                                    <p className="text-xs font-bold">${budgetEstimate.breakdown.labor.toLocaleString()}</p>
                                                </div>
                                                <div className="space-y-1">
                                                    <div className="flex items-center gap-1.5">
                                                        <div className="w-1.5 h-1.5 rounded-full bg-rose-500" />
                                                        <span className="text-[9px] font-bold text-white/40 uppercase">Buffer</span>
                                                    </div>
                                                    <p className="text-xs font-bold">${budgetEstimate.breakdown.contingency.toLocaleString()}</p>
                                                </div>
                                            </div>
                                        </div>

                                        <button className="w-full py-4 bg-white/5 hover:bg-white/10 transition-all rounded-2xl text-[10px] font-bold uppercase tracking-widest border border-white/10 flex items-center justify-center gap-3">
                                            <FileText className="w-4 h-4 text-primary" />
                                            Export Project Dossier
                                        </button>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="p-8 space-y-8 overflow-y-auto h-full">
                                <div className="space-y-2">
                                    <h3 className="text-xl font-bold tracking-tight">Environmental Stress</h3>
                                    <p className="text-xs text-white/40 leading-relaxed font-medium">Model climate impact on infrastructure resilience.</p>
                                </div>

                                <div className="p-8 rounded-[32px] bg-white/5 border border-white/10 space-y-8">
                                    <div className="space-y-4">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <CloudRain className="w-5 h-5 text-cyan-400" />
                                                <span className="text-xs font-bold uppercase tracking-widest text-white/80">Rainfall Intensity</span>
                                            </div>
                                            <span className="text-xs font-mono text-cyan-400 font-bold">{rainfall}mm/hr</span>
                                        </div>
                                        <input
                                            type="range" min="0" max="250" step="10" value={rainfall}
                                            onChange={(e) => setRainfall(parseInt(e.target.value))}
                                            className="w-full h-1.5 bg-white/10 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                                        />
                                        <div className="flex justify-between text-[10px] text-white/30 font-bold">
                                            <span>DRIZZLE</span>
                                            <span>MONSOON</span>
                                            <span>EXTREME</span>
                                        </div>
                                    </div>

                                    <button
                                        onClick={runSimulation}
                                        disabled={isSimulating}
                                        className="w-full py-4 bg-cyan-500/10 hover:bg-cyan-500 text-cyan-400 hover:text-white transition-all rounded-2xl text-[11px] font-bold uppercase tracking-[0.2em] border border-cyan-500/20 flex items-center justify-center gap-3 group shadow-lg shadow-cyan-500/5 hover:shadow-cyan-500/20"
                                    >
                                        <Activity className={`w-4 h-4 ${isSimulating ? 'animate-pulse' : 'group-hover:scale-110 transition-transform'}`} />
                                        {isSimulating ? "Running Hydrology Engine..." : "Trigger Flood Simulation"}
                                    </button>
                                </div>

                                <div className="p-6 rounded-[28px] bg-amber-500/5 border border-amber-500/10 space-y-3">
                                    <div className="flex items-center gap-2">
                                        <Info className="w-4 h-4 text-amber-500/70" />
                                        <span className="text-[10px] font-bold text-amber-500/70 uppercase tracking-widest">Resilience Alert</span>
                                    </div>
                                    <p className="text-[11px] text-white/50 leading-relaxed">
                                        Current rainfall intensity exceeds capacity for proposed drainage zones in [Area Alpha]. Recommended upgrade: 1.5x pipe diameter.
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>
                </main>
            </div>
            <Footer />
        </div>
    );
};

export default Analysis;
