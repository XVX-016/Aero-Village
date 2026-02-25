import React, { Suspense, useState } from "react";
import { Link } from "react-router-dom";
import { Canvas } from "@react-three/fiber";
import { PerspectiveCamera, Environment } from "@react-three/drei";
import * as THREE from "three";
import { DroneModel } from "./DroneModel";

import { GlobalBackground } from "./GlobalBackground";

export const Hero = () => {
    const [isHeroHovered, setIsHeroHovered] = useState(false);

    return (
        <div
            className="relative w-full h-screen overflow-hidden"
            onMouseEnter={() => setIsHeroHovered(true)}
            onMouseLeave={() => setIsHeroHovered(false)}
        >
            <GlobalBackground />

            {/* 3D Background */}
            <div className="absolute inset-0 z-10">
                <Canvas
                    shadows
                    gl={{ antialias: true, toneMapping: THREE.ACESFilmicToneMapping }}
                    onPointerMove={(e) => { e.stopPropagation(); }}
                >
                    <PerspectiveCamera makeDefault position={[0, 0, 8]} fov={45} />
                    <ambientLight intensity={0.5} />
                    <directionalLight position={[5, 5, 5]} intensity={1.8} castShadow />
                    <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={1.2} castShadow />
                    <pointLight position={[-10, -10, -10]} intensity={0.8} color="#bae6fd" />

                    <Suspense fallback={null}>
                        {/* Single Centered Drone */}
                        <DroneModel position={[0, 0, 0]} rotationOffset={0} isHovered={isHeroHovered} />
                    </Suspense>
                </Canvas>
            </div>

            {/* Centered Content Overlay */}
            <div className="absolute inset-0 z-20 flex flex-col items-center justify-center p-4 pointer-events-none">
                <div className="flex flex-col items-center text-center space-y-2 animate-fade-in pointer-events-auto">
                    <span className="text-white/80 italic text-xl md:text-2xl font-light tracking-widest">
                        — A new space —
                    </span>
                    <h1 className="text-8xl md:text-[10rem] font-bold tracking-tighter text-white drop-shadow-2xl leading-none">
                        Aerovillage
                    </h1>
                    <div className="relative group">
                        <div className="absolute inset-0 bg-white/20 blur-xl group-hover:bg-white/30 transition-all rounded-full" />
                        <p className="relative text-xl md:text-2xl font-medium text-white px-8 py-3 rounded-full border border-white/30 backdrop-blur-md">
                            Smart Village Intelligence anywhere in the world, in real-time.
                        </p>
                    </div>
                </div>
            </div>

            {/* Bottom Links / Scroll Indicator */}
            <div className="absolute bottom-12 left-0 right-0 z-20 flex justify-center pointer-events-none">
                <Link to="/upload" className="px-10 py-4 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-full border border-white/20 backdrop-blur-md transition-all transform hover:scale-105 pointer-events-auto">
                    Explore Platform
                </Link>
            </div>
        </div>
    );
};
