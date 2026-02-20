import React, { useState } from "react";
import { Upload as UploadIcon, FileJson, Map as MapIcon, Database } from "lucide-react";
import Navbar from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { GlobalBackground } from "@/components/GlobalBackground";

const Upload = () => {
    const [isDragging, setIsDragging] = useState(false);

    return (
        <div className="min-h-screen bg-secondary/20 flex flex-col relative">
            <GlobalBackground />
            <Navbar />
            <main className="flex-grow container mx-auto px-4 py-24 mt-20 relative z-10">
                <div className="max-w-4xl mx-auto space-y-12">
                    {/* Header */}
                    <div className="text-center space-y-4">
                        <h1 className="text-5xl font-bold text-secondary">Spatial Data Extraction</h1>
                        <p className="text-muted-foreground text-xl">Upload your orthophoto or drone imagery to begin AI analysis.</p>
                    </div>

                    {/* Upload Zone */}
                    <div
                        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                        onDragLeave={() => setIsDragging(false)}
                        onDrop={(e) => { e.preventDefault(); setIsDragging(false); }}
                        className={`
              h-96 rounded-[40px] border-2 border-dashed transition-all duration-300 flex flex-col items-center justify-center space-y-6
              ${isDragging ? "border-primary bg-primary/5 scale-[1.02]" : "border-border bg-card/50 backdrop-blur-sm"}
              hover:border-primary/50 group cursor-pointer
            `}
                    >
                        <div className={`p-6 rounded-3xl ${isDragging ? "bg-primary text-white" : "bg-muted text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary"} transition-colors shadow-sm`}>
                            <UploadIcon className="w-12 h-12" />
                        </div>
                        <div className="text-center">
                            <p className="text-xl font-bold text-secondary uppercase tracking-tight">Drag and drop drone imagery</p>
                            <p className="text-muted-foreground font-medium">Supports .tif, .jpg, .png up to 5GB</p>
                        </div>
                        <button className="px-10 py-4 bg-secondary text-white rounded-full font-bold hover:bg-secondary/90 hover:scale-105 transition-all shadow-xl shadow-secondary/10">
                            SELECT FILES
                        </button>
                    </div>

                    {/* Placeholder Dashboard Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 opacity-50 pointer-events-none">
                        {[
                            { label: "Coordinates", value: "34.123, -118.456", icon: <MapIcon /> },
                            { label: "Vegetation Index", value: "0.82 NDVI", icon: <Database /> },
                            { label: "Detected Footprints", value: "Wait for upload...", icon: <FileJson /> }
                        ].map((stat, i) => (
                            <div key={i} className="p-6 rounded-3xl border border-border bg-card flex items-center space-x-4">
                                <div className="p-3 rounded-2xl bg-muted text-secondary">{stat.icon}</div>
                                <div>
                                    <p className="text-sm text-muted-foreground">{stat.label}</p>
                                    <p className="text-lg font-bold text-secondary">{stat.value}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </main>
            <Footer />
        </div>
    );
};

export default Upload;
