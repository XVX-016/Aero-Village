import React from "react";
import Navbar from "@/components/Navbar";
import { Hero } from "@/components/Hero";
import { Capabilities } from "@/components/Capabilities";
import { Philosophy } from "@/components/Philosophy";
import { Footer } from "@/components/Footer";

const Index = () => {
  return (
    <main className="min-h-screen">
      <Navbar />
      <div className="relative z-10">
        <Hero />
        <Capabilities />
        <Philosophy />
        <Footer />
      </div>
    </main>
  );
};

export default Index;
