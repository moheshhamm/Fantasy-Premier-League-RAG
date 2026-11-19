"use client";

import { cn } from "@/lib/utils";

interface LoadingAnimationProps {
  className?: string;
}

export function LoadingAnimation({ className }: LoadingAnimationProps) {
  return (
    <div className={cn(
      "flex flex-col items-center justify-center py-20 gap-8",
      className
    )}>
      {/* Animated orb */}
      <div className="relative w-24 h-24">
        {/* Outer glow ring */}
        <div className="absolute inset-0 rounded-full bg-neon/10 animate-ping" />
        
        {/* Rotating ring */}
        <div className="absolute inset-2 rounded-full border border-neon/30 animate-[spin_3s_linear_infinite]">
          <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-neon shadow-[0_0_10px_rgba(0,255,170,0.8)]" />
        </div>
        
        {/* Inner rotating ring (reverse) */}
        <div className="absolute inset-4 rounded-full border border-neon-secondary/30 animate-[spin_2s_linear_infinite_reverse]">
          <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-neon-secondary shadow-[0_0_8px_rgba(0,200,200,0.8)]" />
        </div>
        
        {/* Center orb */}
        <div className="absolute inset-8 rounded-full bg-gradient-to-br from-neon/40 to-neon-secondary/40 backdrop-blur-sm animate-pulse" />
      </div>
      
      {/* Status text */}
      <div className="text-center space-y-2">
        <p className="text-lg font-medium text-foreground">Processing query</p>
        <p className="text-sm text-muted-foreground max-w-xs mx-auto">
          Running inference across selected models and analyzing knowledge graphs
        </p>
      </div>
      
      {/* Progress indicator */}
      <div className="flex items-center gap-2">
        {[0, 1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="w-2 h-2 rounded-full bg-neon/60"
            style={{
              animation: "pulse 1.5s ease-in-out infinite",
              animationDelay: `${i * 0.15}s`,
            }}
          />
        ))}
      </div>
    </div>
  );
}
