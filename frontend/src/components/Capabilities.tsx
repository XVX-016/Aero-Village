import React from "react";
import { motion } from "framer-motion";
import { Layout, Cpu, LineChart, FileOutput } from "lucide-react";

const capabilities = [
    {
        icon: <Cpu className="w-8 h-8 text-[#003366]" />,
        title: "ML Data Extraction",
        description: "Automatically detect buildings, roads, vegetation, and water bodies.",
        spec: "AI Powered"
    },
    {
        icon: <Layout className="w-8 h-8 text-[#003366]" />,
        title: "RAG Planning Engine",
        description: "Suggest optimal sewage, electricity, and road layouts using AI.",
        spec: "Suggestive AI"
    },
    {
        icon: <LineChart className="w-8 h-8 text-[#003366]" />,
        title: "Village Analytics",
        description: "Real-time stats: building density, NDVI vegetation index, infrastructure coverage.",
        spec: "Live Analysis"
    },
    {
        icon: <FileOutput className="w-8 h-8 text-[#003366]" />,
        title: "Data Export",
        description: "Export ML outputs and planning suggestions in GIS, CSV, or PDF formats.",
        spec: "Multi-Format"
    }
];

export const Capabilities = () => {
    return (
        <section className="py-24 relative overflow-hidden bg-transparent">
            {/* Background blur to create glass effect over the hero image if it extends */}
            <div className="absolute inset-0 bg-white/5 backdrop-blur-[2px]" />

            <div className="container mx-auto px-4 relative z-10">
                <div className="text-center mb-16 px-4">
                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-4 drop-shadow-lg">System Capabilities</h2>
                    <p className="text-white/80 text-lg max-w-2xl mx-auto font-medium">
                        Empowering rural transformation with state-of-the-art spatial intelligence.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {capabilities.map((cap, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: index * 0.1 }}
                            className="p-8 rounded-[32px] glass-card hover:translate-y-[-8px] group flex flex-col items-center text-center justify-between h-full"
                        >
                            <div className="mb-6 p-4 rounded-2xl bg-white/10 group-hover:bg-[#003366]/20 transition-colors w-fit">
                                {cap.icon}
                            </div>
                            <h3 className="text-xl font-bold text-white mb-3 tracking-tight">{cap.title}</h3>
                            <p className="text-white/70 mb-6 line-clamp-3 leading-relaxed text-sm font-medium">{cap.description}</p>
                            <div className="text-[10px] font-bold text-[#003366] uppercase tracking-[0.2em] bg-[#003366]/10 w-fit px-3 py-1 rounded-full border border-[#003366]/20 mt-auto">
                                {cap.spec}
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};
