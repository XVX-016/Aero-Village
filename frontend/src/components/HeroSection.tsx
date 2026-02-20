import { motion, useMotionValue, useTransform } from "framer-motion";
import { useEffect } from "react";
import heroBg from "@/assets/hero-bg.png";
import droneImg from "@/assets/drone.png";

const HeroSection = () => {
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const rotateX = useTransform(mouseY, [0, 1], [8, -8]);
  const rotateY = useTransform(mouseX, [0, 1], [-8, 8]);

  useEffect(() => {
    const handleMouse = (e: MouseEvent) => {
      mouseX.set(e.clientX / window.innerWidth);
      mouseY.set(e.clientY / window.innerHeight);
    };
    window.addEventListener("mousemove", handleMouse);
    return () => window.removeEventListener("mousemove", handleMouse);
  }, [mouseX, mouseY]);

  return (
    <section className="relative min-h-screen flex items-center overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0">
        <img
          src={heroBg}
          alt="Rolling hills landscape"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-background/30 via-transparent to-background" />
      </div>

      <div className="container mx-auto px-6 relative z-10 pt-24">
        <div className="grid lg:grid-cols-2 gap-12 items-center min-h-[70vh]">
          {/* Left - Text */}
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            <motion.span
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="inline-block px-4 py-1.5 rounded-full bg-accent text-secondary text-xs font-semibold mb-6 tracking-wide uppercase"
            >
              Smart Village Platform
            </motion.span>

            <h1 className="text-5xl md:text-6xl lg:text-7xl font-extrabold text-secondary leading-tight mb-6">
              Building
              <br />
              <span className="text-primary">Smarter</span>
              <br />
              Villages
            </h1>

            <p className="text-lg text-muted-foreground max-w-md mb-8 leading-relaxed">
              AI-powered data extraction, planning, and analysis to transform rural communities into thriving smart villages.
            </p>

            <div className="flex flex-wrap gap-4">
              <button className="px-8 py-3.5 rounded-full bg-primary text-primary-foreground font-semibold text-sm shadow-lg hover:shadow-xl transition-shadow glow-primary">
                Explore Village
              </button>
              <button className="px-8 py-3.5 rounded-full border border-border bg-card/80 backdrop-blur-sm text-secondary font-semibold text-sm hover:bg-card transition-colors">
                Learn More
              </button>
            </div>
          </motion.div>

          {/* Right - Drone */}
          <div className="flex items-center justify-center">
            <motion.div
              style={{ rotateX, rotateY, perspective: 600 }}
              animate={{ y: [0, -20, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
              className="w-72 h-72 md:w-96 md:h-96"
            >
              <img
                src={droneImg}
                alt="SmaVita Drone"
                className="w-full h-full object-contain drop-shadow-2xl"
              />
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
