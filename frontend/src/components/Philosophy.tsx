import React from "react";

export const Philosophy = () => {
    return (
        <section className="py-24 bg-transparent text-white overflow-hidden relative">
            <div className="container mx-auto px-4 relative z-10">
                <div className="max-w-5xl mx-auto glass-card p-12 md:p-20 rounded-[48px] border-white/20 shadow-2xl space-y-12">
                    <div className="text-center space-y-8">
                        <h2 className="text-sm font-bold text-[#003366] uppercase tracking-[0.3em] opacity-80">OUR MISSION</h2>
                        <div className="space-y-6">
                            <p className="text-4xl md:text-6xl font-bold leading-tight tracking-tighter">
                                Mapping the future of <span className="text-[#003366] italic">rural governance</span>, one footprint at a time.
                            </p>
                            <p className="text-lg md:text-xl text-white/70 font-medium leading-relaxed max-w-2xl mx-auto pt-4">
                                Aerovillage is more than a mapping tool. It's an intelligence platform designed to bridge the gap between
                                aerial data and actionable social impact, ensuring every village is seen, mapped, and empowered.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Background patterns */}
            <div className="absolute top-0 right-0 w-full h-full opacity-10 pointer-events-none">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] border border-white rounded-full animate-ping [animation-duration:10s]" />
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] border border-white rounded-full animate-ping [animation-duration:8s]" />
            </div>
        </section>
    );
};
