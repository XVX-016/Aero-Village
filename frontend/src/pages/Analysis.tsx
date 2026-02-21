import React, { useState } from "react";
import { Send, Bot, User, Map as MapIcon, Maximize2, Share2 } from "lucide-react";
import { Footer } from "@/components/Footer";
import Navbar from "@/components/Navbar";
import { GlobalBackground } from "@/components/GlobalBackground";

const Analysis = () => {
    const [messages, setMessages] = useState([
        { role: "assistant", content: "Platform ready. You can query spatial intelligence or infrastructure layout." }
    ]);
    const [input, setInput] = useState("");

    const handleSend = () => {
        if (!input.trim()) return;
        setMessages(prev => [...prev, { role: "user", content: input }]);
        setTimeout(() => {
            setMessages(prev => [...prev, { role: "assistant", content: "Analyzing spatial data... This query would be processed via the RAG engine in production." }]);
        }, 1000);
        setInput("");
    };

    return (
        <div className="min-h-screen flex flex-col bg-secondary/10 relative">
            <GlobalBackground />
            <Navbar />
            <div className="flex-grow flex flex-col pt-16 relative z-10">
                {/* Top Header */}
                <header className="h-20 border-b border-white/10 flex items-center justify-between px-8 shrink-0 bg-[#0B1215]/80 backdrop-blur-md">
                    <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-white font-bold shadow-lg shadow-primary/20">S</div>
                        <h1 className="text-xl font-bold text-white tracking-tight font-outfit uppercase">SMAVITA Command Center</h1>
                    </div>
                    <div className="flex items-center space-x-6">
                        <div className="flex items-center space-x-2">
                            <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
                            <span className="text-xs font-bold text-emerald-500 uppercase tracking-widest">System Live</span>
                        </div>
                        <div className="flex space-x-2">
                            <button className="p-2 hover:bg-white/10 rounded-lg transition-colors text-white/70 hover:text-white"><Share2 className="w-5 h-5" /></button>
                            <button className="p-2 hover:bg-white/10 rounded-lg transition-colors text-white/70 hover:text-white"><Maximize2 className="w-5 h-5" /></button>
                        </div>
                    </div>
                </header>

                {/* Main Container */}
                <main className="flex-grow flex overflow-hidden">
                    {/* Map View Placeholder - 70% */}
                    <div className="flex-grow bg-[#0B1215] relative group overflow-hidden border-r border-white/5">
                        <div className="absolute inset-0 flex items-center justify-center">
                            <div className="text-center space-y-4">
                                <MapIcon className="w-20 h-20 text-white/5 mx-auto" />
                                <p className="text-white/10 font-bold tracking-[0.2em] uppercase">GIS MASTER VIEWPORT</p>
                            </div>
                        </div>

                        {/* Overlay Controls */}
                        <div className="absolute top-6 left-6 flex flex-col space-y-4">
                            <div className="p-4 glass rounded-3xl space-y-3 max-w-xs shadow-elegant border-white/10">
                                <p className="text-[10px] font-bold text-primary uppercase tracking-widest">Active Survey</p>
                                <p className="text-sm font-bold text-white">Wynnpage Drive Survey</p>
                                <div className="h-px bg-white/10 w-full" />
                                <div className="space-y-2">
                                    <button className="w-full flex items-center justify-between text-[11px] font-bold text-white/70 hover:text-[#FFD700] transition-colors">
                                        ELECTRICAL GRID <div className="w-2 h-2 rounded-full bg-[#FFD700]" />
                                    </button>
                                    <button className="w-full flex items-center justify-between text-[11px] font-bold text-white/70 hover:text-[#00F5FF] transition-colors">
                                        WATER FLOW <div className="w-2 h-2 rounded-full bg-[#00F5FF]" />
                                    </button>
                                    <button className="w-full flex items-center justify-between text-[11px] font-bold text-white/70 hover:text-[#2ECC71] transition-colors">
                                        VEGETATION <div className="w-2 h-2 rounded-full bg-[#2ECC71]" />
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Coordinate Overlay */}
                        <div className="absolute bottom-6 left-6 px-4 py-2 glass rounded-full border-white/10">
                            <p className="text-[10px] font-mono text-white/50 tracking-wider">LAT: 34.1235478 | LON: -118.4568921 | ALT: 124m</p>
                        </div>
                    </div>

                    {/* Data Analysis Sidebar - 30% */}
                    <div className="w-96 flex flex-col bg-[#0B1215] shrink-0">
                        {/* Top Status Bar */}
                        <div className="p-4 border-b border-white/10 bg-white/5">
                            <p className="text-[10px] font-bold text-white/40 uppercase tracking-widest mb-2">RAG Analysis Results</p>
                            <div className="flex items-center justify-between">
                                <span className="text-xs font-bold text-white">Infrastructure Health</span>
                                <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-500 text-[10px] font-bold uppercase">Optimal</span>
                            </div>
                        </div>

                        {/* Insight Cards / Chat */}
                        <div className="flex-grow overflow-y-auto p-6 space-y-6">
                            {/* Insight Card Example */}
                            <div className="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-3">
                                <div className="flex items-center justify-between">
                                    <span className="text-[10px] font-bold text-primary uppercase">Observation</span>
                                    <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-500 text-[10px] font-bold uppercase">Priority High</span>
                                </div>
                                <p className="text-xs text-white leading-relaxed">
                                    Open trench detected at coordinates [34.123, -118.456]. Infrastructure risk high.
                                </p>
                                <div className="h-px bg-white/10 w-full" />
                                <p className="text-[10px] text-white/50 italic">
                                    Suggestion: Immediate pipeline reinforcement recommended before monsoon season.
                                </p>
                            </div>

                            {messages.map((msg, i) => (
                                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                    <div className={`flex items-start space-x-3 max-w-[90%]`}>
                                        {msg.role === 'assistant' && (
                                            <div className="w-7 h-7 rounded-lg bg-primary/20 text-primary flex items-center justify-center shrink-0">
                                                <Bot className="w-4 h-4" />
                                            </div>
                                        )}
                                        <div className={`
                                            p-3 rounded-2xl text-[13px] leading-relaxed
                                            ${msg.role === 'user' ? 'bg-primary text-white font-medium' : 'bg-white/5 text-white/80 border border-white/10'}
                                        `}>
                                            {msg.content}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Chat Input */}
                        <div className="p-6 border-t border-white/10">
                            <div className="relative">
                                <input
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                    type="text"
                                    placeholder="Input spatial query..."
                                    className="w-full bg-white/5 border-white/10 text-white placeholder:text-white/30 focus:border-primary focus:ring-0 rounded-xl py-3 pl-5 pr-12 text-sm transition-all"
                                />
                                <button
                                    onClick={handleSend}
                                    className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 bg-primary text-white rounded-lg hover:shadow-lg hover:shadow-primary/20 transition-all"
                                >
                                    <Send className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    </div>
                </main>
                <Footer />
            </div>
        </div>
    );
};
export default Analysis;
