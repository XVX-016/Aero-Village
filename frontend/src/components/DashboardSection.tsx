import { motion } from "framer-motion";
import { Upload, Send, Bot, FileImage } from "lucide-react";
import { useState } from "react";

const sampleMessages = [
  { role: "assistant" as const, text: "Welcome to SmaVita RAG Analysis. Upload village data or ask me anything about smart village planning." },
];

const DashboardSection = () => {
  const [messages] = useState(sampleMessages);
  const [input, setInput] = useState("");

  return (
    <section id="dashboard" className="py-24 px-6">
      <div className="container mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-secondary mb-4">
            SmaVita Dashboard
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Upload imagery, extract insights, and interact with our AI analysis engine.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {/* Upload Area */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="glass-card rounded-3xl p-8 flex flex-col items-center justify-center min-h-[400px]"
          >
            <div className="border-2 border-dashed border-primary/30 rounded-3xl w-full h-full flex flex-col items-center justify-center gap-6 p-8 hover:border-primary/60 transition-colors cursor-pointer">
              <motion.div
                animate={{ scale: [1, 1.05, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="w-20 h-20 rounded-full bg-accent flex items-center justify-center"
              >
                <Upload className="w-10 h-10 text-primary" />
              </motion.div>
              <div className="text-center">
                <h3 className="text-xl font-semibold text-secondary mb-2">Upload Village Data</h3>
                <p className="text-muted-foreground text-sm">
                  Drag & drop satellite images, surveys, or documents
                </p>
              </div>
              <div className="flex gap-3">
                <span className="px-3 py-1.5 rounded-full bg-accent text-xs font-medium text-secondary flex items-center gap-1.5">
                  <FileImage className="w-3.5 h-3.5" /> Images
                </span>
                <span className="px-3 py-1.5 rounded-full bg-accent text-xs font-medium text-secondary">
                  PDF
                </span>
                <span className="px-3 py-1.5 rounded-full bg-accent text-xs font-medium text-secondary">
                  CSV
                </span>
              </div>
            </div>
          </motion.div>

          {/* Chat Sidebar */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="glass-card rounded-3xl p-6 flex flex-col min-h-[400px]"
          >
            <div className="flex items-center gap-3 mb-6 pb-4 border-b border-border">
              <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
                <Bot className="w-5 h-5 text-primary-foreground" />
              </div>
              <div>
                <h3 className="font-semibold text-secondary">RAG Analysis</h3>
                <p className="text-xs text-muted-foreground">AI-powered village insights</p>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto space-y-4 mb-4">
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex ${msg.role === "assistant" ? "justify-start" : "justify-end"}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                      msg.role === "assistant"
                        ? "bg-muted text-foreground"
                        : "bg-primary text-primary-foreground"
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>
              ))}
            </div>

            <div className="flex items-center gap-2 bg-muted rounded-2xl p-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about village data..."
                className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground px-3 py-2 outline-none"
              />
              <button className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center hover:opacity-90 transition-opacity shrink-0">
                <Send className="w-4 h-4 text-primary-foreground" />
              </button>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default DashboardSection;
