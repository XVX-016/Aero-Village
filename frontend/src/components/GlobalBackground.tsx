import React from "react";

export const GlobalBackground = () => {
    return (
        <div className="fixed inset-0 z-0 pointer-events-none">
            <img
                src="/drone-bg.png"
                alt="Global Background"
                className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-blue-500/10 backdrop-blur-[2px]" />
        </div>
    );
};
