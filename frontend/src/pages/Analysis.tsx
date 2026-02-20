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
                <header className="h-20 border-b border-border flex items-center justify-between px-8 shrink-0 bg-card/80 backdrop-blur-md">
                    <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-white font-bold shadow-lg shadow-primary/20">S</div>
                        <h1 className="text-xl font-bold text-secondary tracking-tight font-outfit uppercase">SMAVITA Intelligence Hub</h1>
                    </div>
                    <div className="flex space-x-2">
                        <button className="p-2 hover:bg-muted rounded-lg transition-colors"><Share2 className="w-5 h-5" /></button>
                        <button className="p-2 hover:bg-muted rounded-lg transition-colors"><Maximize2 className="w-5 h-5" /></button>
                    </div>
                </header>

                {/* Main Container */}
                <main className="flex-grow flex overflow-hidden">
                    {/* Map View Placeholder */}
                    <div className="flex-grow bg-muted relative group overflow-hidden">
                        <div className="absolute inset-0 flex items-center justify-center">
                            <div className="text-center space-y-4">
                                <MapIcon className="w-16 h-16 text-muted-foreground/30 mx-auto" />
                                <p className="text-muted-foreground/50 font-medium">GIS VIEWPORT ENABLED</p>
                            </div>
                        </div>
                        <div className="absolute top-6 left-6 p-4 glass rounded-2xl space-y-2 max-w-xs shadow-elegant">
                            <p className="text-xs font-bold text-primary uppercase tracking-widest">Active Survey</p>
                            <p className="text-sm font-semibold">Wynnpage Drive Survey</p>
                        </div>
                    </div>

                    {/* Chat Sidebar */}
                    <div className="w-[450px] border-l border-border flex flex-col bg-card shrink-0">
                        {/* Chat History */}
                        <div className="flex-grow overflow-y-auto p-6 space-y-6">
                            {messages.map((msg, i) => (
                                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                    <div className={`flex items-start space-x-3 max-w-[85%]`}>
                                        {msg.role === 'assistant' && (
                                            <div className="w-8 h-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
                                                <Bot className="w-5 h-5" />
                                            </div>
                                        )}
                                        <div className={`
                    p-4 rounded-3xl text-sm leading-relaxed
                    ${msg.role === 'user' ? 'bg-primary text-white' : 'bg-muted text-secondary'}
                  `}>
                                            {msg.content}
                                        </div>
                                        {msg.role === 'user' && (
                                            <div className="w-8 h-8 rounded-lg bg-secondary text-white flex items-center justify-center shrink-0">
                                                <User className="w-5 h-5" />
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Chat Input */}
                        <div className="p-6 border-t border-border">
                            <div className="relative group">
                                <input
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                    type="text"
                                    placeholder="Ask Nexus Planner..."
                                    className="w-full bg-muted border-transparent focus:border-primary focus:ring-0 rounded-2xl py-4 pl-6 pr-14 transition-all"
                                />
                                <button
                                    onClick={handleSend}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-primary text-white rounded-xl hover:shadow-lg hover:shadow-primary/20 transition-all"
                                >
                                    <Send className="w-5 h-5" />
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
