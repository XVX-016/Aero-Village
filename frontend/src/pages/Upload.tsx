import React, { useState } from "react";
import { Upload as UploadIcon, Map as MapIcon, Layers, Expand, ShieldCheck, Info } from "lucide-react";
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import Navbar from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { GlobalBackground } from "@/components/GlobalBackground";

const Upload = () => {
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<null | 'success' | 'error'>(null);
    const [spatialMeta, setSpatialMeta] = useState<any>(null);
    const [opacity, setOpacity] = useState(0.8);
    const [radius, setRadius] = useState(1);
    const fileInputRef = React.useRef<HTMLInputElement>(null);
    const mapContainer = React.useRef<HTMLDivElement>(null);
    const map = React.useRef<maplibregl.Map | null>(null);

    React.useEffect(() => {
        if (!mapContainer.current || map.current) return;

        map.current = new maplibregl.Map({
            container: mapContainer.current,
            style: 'https://demotiles.maplibre.org/style.json', // Use a free satellite style in production
            center: [78.9629, 20.5937], // India default
            zoom: 4
        });

        map.current.addControl(new maplibregl.NavigationControl({}));

        return () => {
            map.current?.remove();
            map.current = null;
        };
    }, []);

    const handleUpload = async (files: FileList | null) => {
        if (!files || files.length === 0) return;

        setIsUploading(true);
        setUploadStatus(null);
        setSpatialMeta(null);

        const formData = new FormData();
        formData.append('file', files[0]);

        try {
            const response = await fetch('http://localhost:8000/api/upload', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            if (response.ok) {
                setUploadStatus('success');
                setSpatialMeta(data.spatial_metadata || { has_spatial: false });

                if (data.spatial_metadata?.has_spatial && map.current && data.spatial_metadata.bounds) {
                    const bounds = data.spatial_metadata.bounds;
                    map.current.fitBounds([
                        [bounds[0], bounds[1]],
                        [bounds[2], bounds[3]]
                    ]);
                }
            } else {
                setUploadStatus('error');
            }
        } catch (error) {
            console.error('Upload failed:', error);
            setUploadStatus('error');
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#0B1215]/20 flex flex-col relative text-white">
            <GlobalBackground />
            <Navbar />
            <main className="flex-grow container mx-auto px-4 py-24 mt-20 relative z-10">
                <div className="max-w-6xl mx-auto grid lg:grid-cols-2 gap-12">
                    {/* Left - Upload & Controls */}
                    <div className="space-y-8">
                        <div className="space-y-4">
                            <h1 className="text-5xl font-bold tracking-tighter">Spatial Ingestion</h1>
                            <p className="text-[#A0AEC0] text-xl font-medium leading-relaxed">
                                Upload drone imagery for mission-critical AI extraction & infrastructure planning.
                            </p>
                        </div>

                        <div
                            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                            onDragLeave={() => setIsDragging(false)}
                            onDrop={(e) => {
                                e.preventDefault();
                                setIsDragging(false);
                                handleUpload(e.dataTransfer.files);
                            }}
                            onClick={() => fileInputRef.current?.click()}
                            className={`
                                h-80 rounded-[40px] border-2 border-dashed transition-all duration-300 flex flex-col items-center justify-center space-y-6
                                ${isDragging ? "border-primary bg-primary/5 scale-[1.02]" : "border-white/10 bg-[#0B1215]/50 backdrop-blur-md"}
                                ${isUploading ? "opacity-50 pointer-events-none" : "hover:border-primary/50 cursor-pointer"}
                                group shadow-2xl relative overflow-hidden
                            `}
                        >
                            <input
                                type="file"
                                ref={fileInputRef}
                                style={{ display: 'none' }}
                                onChange={(e) => handleUpload(e.target.files)}
                                accept=".tif,.jpg,.jpeg,.png"
                            />

                            <div className={`p-6 rounded-3xl ${isDragging ? "bg-primary text-white" : "bg-white/5 text-white/30 group-hover:bg-primary/10 group-hover:text-primary"} transition-colors shadow-sm`}>
                                {isUploading ? (
                                    <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin" />
                                ) : (
                                    <UploadIcon className="w-10 h-10" />
                                )}
                            </div>
                            <div className="text-center px-8">
                                <p className="text-lg font-bold uppercase tracking-tight">
                                    {isUploading ? "Verifying Geospatial Integrity..." : "Select GeoTIFF or Drone imagery"}
                                </p>
                                <p className="text-[#A0AEC0] text-sm font-medium mt-1">
                                    {uploadStatus === 'success' ? "Spatial Metadata Extracted!" : "EPSG:4326, 3857, or manual alignment"}
                                </p>
                            </div>
                        </div>

                        {/* Spatial Controls */}
                        {spatialMeta && (
                            <div className="p-8 rounded-[32px] bg-[#0B1215]/80 backdrop-blur-xl border border-white/10 space-y-6 animate-fade-in shadow-2xl">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-500">
                                            <ShieldCheck className="w-5 h-5" />
                                        </div>
                                        <span className="text-sm font-bold uppercase tracking-widest">Geo-Validation</span>
                                    </div>
                                    <span className="text-[10px] font-bold px-2 py-1 rounded bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">VALID READY</span>
                                </div>

                                <div className="space-y-4">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2 text-white/70">
                                            <Layers className="w-4 h-4" />
                                            <span className="text-xs font-bold uppercase tracking-tight">Image Opacity</span>
                                        </div>
                                        <span className="text-[10px] font-mono text-primary font-bold">{Math.round(opacity * 100)}%</span>
                                    </div>
                                    <input
                                        type="range" min="0" max="1" step="0.01" value={opacity}
                                        onChange={(e) => setOpacity(parseFloat(e.target.value))}
                                        className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-primary"
                                    />
                                </div>

                                <div className="space-y-4">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2 text-white/70">
                                            <Expand className="w-4 h-4" />
                                            <span className="text-xs font-bold uppercase tracking-tight">Area Amplification</span>
                                        </div>
                                        <span className="text-[10px] font-mono text-primary font-bold">{radius}km Buffer</span>
                                    </div>
                                    <div className="grid grid-cols-3 gap-2">
                                        {[0.5, 1, 5].map(r => (
                                            <button
                                                key={r} onClick={() => setRadius(r)}
                                                className={`py-2 rounded-xl text-[10px] font-bold border transition-all ${radius === r ? 'bg-primary border-primary text-white scale-105 shadow-lg' : 'border-white/10 text-white/50 hover:border-white/20'}`}
                                            >
                                                {r}KM
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <button className="w-full py-4 bg-primary text-white rounded-2xl font-bold hover:shadow-xl hover:shadow-primary/20 transition-all uppercase tracking-widest text-[11px] mt-4 hover:scale-[1.02] active:scale-95">
                                    Trigger Extraction Pipeline
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Right - Interactive Map Viewport */}
                    <div className="h-full min-h-[500px] rounded-[48px] bg-[#0B1215] relative overflow-hidden group border border-white/5 shadow-2xl">
                        <div ref={mapContainer} className="absolute inset-0" />

                        {!spatialMeta && (
                            <div className="absolute inset-0 flex items-center justify-center p-12 text-center bg-[#0B1215]/40 backdrop-blur-sm z-20">
                                <div className="space-y-4 translate-y-[-10px]">
                                    <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center mx-auto border border-white/10">
                                        <MapIcon className="w-10 h-10 text-white/20" />
                                    </div>
                                    <p className="text-white/40 font-bold uppercase tracking-widest text-xs">Awaiting Spatial Input</p>
                                </div>
                            </div>
                        )}

                        {spatialMeta && (
                            <div className="absolute top-8 right-8 p-5 glass rounded-[28px] border-white/10 space-y-3 pointer-events-none z-20 backdrop-blur-2xl">
                                <div className="flex items-center gap-2">
                                    <Info className="w-4 h-4 text-primary" />
                                    <span className="text-[10px] font-bold text-white uppercase tracking-widest">Extraction Metadata</span>
                                </div>
                                <div className="text-[10px] font-mono text-white/50 leading-relaxed font-bold">
                                    CRS: {spatialMeta.crs?.slice(0, 18) || "N/A"}...<br />
                                    COORD: {spatialMeta.bounds?.[0].toFixed(4) || "0.0000"}, {spatialMeta.bounds?.[1].toFixed(4) || "0.0000"}
                                </div>
                            </div>
                        )}

                        {/* Map Overlay HUD */}
                        <div className="absolute bottom-8 left-8 p-3 bg-[#0B1215]/80 backdrop-blur-md rounded-2xl border border-white/10 z-20">
                            <span className="text-[9px] font-bold uppercase tracking-tighter text-white/40">Viewport Status: Live Satellite</span>
                        </div>
                    </div>
                </div>
            </main>
            <Footer />
        </div>
    );
};

export default Upload;
