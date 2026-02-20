import { useState } from "react";
import { Menu, X } from "lucide-react";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/20 backdrop-blur-[20px] bg-white/[0.03] shadow-lg">
      <div className="container mx-auto px-6 py-4 flex items-center justify-between">
        <a href="/" className="text-2xl font-bold text-white uppercase tracking-tighter flex items-center gap-2">
          <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-xl">
            <div className="w-4 h-4 bg-white rounded-sm rotate-45" />
          </div>
          SMAVITA
        </a>

        <div className="hidden md:flex items-center gap-10">
          <a href="/upload" className="text-sm font-semibold text-white/80 hover:text-white transition-all uppercase tracking-widest">
            Upload
          </a>
          <a href="/analysis" className="text-sm font-semibold text-white/80 hover:text-white transition-all uppercase tracking-widest">
            Analysis
          </a>
          <button className="px-6 py-2 rounded-full border border-white/30 text-white font-semibold hover:bg-white hover:text-blue-600 transition-all text-sm">
            Sign Up
          </button>
        </div>

        <button
          className="md:hidden text-white"
          onClick={() => setIsOpen(!isOpen)}
        >
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {isOpen && (
        <div className="md:hidden px-6 pb-6 flex flex-col gap-4 border-t border-white/10 bg-blue-900/40 backdrop-blur-xl">
          <a href="/upload" className="text-sm font-semibold text-white/90 pt-4">UPLOAD</a>
          <a href="/analysis" className="text-sm font-semibold text-white/90">ANALYSIS</a>
          <button className="w-full px-5 py-3 rounded-full bg-white text-blue-900 font-bold text-sm">
            SIGN UP
          </button>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
