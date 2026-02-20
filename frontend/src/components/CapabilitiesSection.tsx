import { motion } from "framer-motion";
import { Database, Map, BrainCircuit } from "lucide-react";

const capabilities = [
  {
    icon: Database,
    title: "Data Extraction",
    description: "Automatically extract and process village data from satellite imagery, surveys, and government records with AI-powered pipelines.",
  },
  {
    icon: Map,
    title: "Village Planning",
    description: "Generate smart infrastructure plans, resource allocation maps, and development roadmaps tailored to each village's unique needs.",
  },
  {
    icon: BrainCircuit,
    title: "RAG Analysis",
    description: "Ask questions about village data using our Retrieval-Augmented Generation engine for instant, accurate insights and recommendations.",
  },
];

const CapabilitiesSection = () => {
  return (
    <section id="capabilities" className="py-24 px-6 bg-muted/50">
      <div className="container mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-secondary mb-4">
            Capabilities
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Empowering smart village development with cutting-edge AI and data tools.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {capabilities.map((cap, index) => (
            <motion.div
              key={cap.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.15 }}
              viewport={{ once: true }}
              whileHover={{ y: -8, scale: 1.02 }}
              className="glass-card rounded-3xl p-8 cursor-default group transition-shadow hover:shadow-xl"
            >
              <div className="w-14 h-14 rounded-2xl bg-accent flex items-center justify-center mb-6 group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                <cap.icon className="w-7 h-7 text-primary group-hover:text-primary-foreground transition-colors" />
              </div>
              <h3 className="text-xl font-bold text-secondary mb-3">{cap.title}</h3>
              <p className="text-muted-foreground leading-relaxed">{cap.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default CapabilitiesSection;
