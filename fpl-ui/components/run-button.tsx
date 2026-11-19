"use client";

import { cn } from "@/lib/utils";
import { Sparkles, Loader2, ArrowRight } from "lucide-react";

interface RunButtonProps {
  onClick: () => void;
  isLoading: boolean;
  disabled?: boolean;
}

export function RunButton({
  onClick,
  isLoading,
  disabled = false,
}: RunButtonProps) {
  return (
    <div className="relative group">
      {/* Animated glow background */}
      <div
        className={cn(
          "absolute -inset-1 rounded-2xl blur-lg transition-all duration-500",
          "bg-gradient-to-r from-neon via-neon-secondary to-neon",
          disabled || isLoading ? "opacity-0" : "opacity-30 group-hover:opacity-50"
        )}
      />
      
      <button
        onClick={onClick}
        disabled={disabled || isLoading}
        className={cn(
          "relative w-full flex items-center justify-center gap-3",
          "h-14 px-8 rounded-2xl",
          "text-lg font-semibold",
          "transition-all duration-300",
          "disabled:cursor-not-allowed",
          disabled || isLoading
            ? "bg-secondary text-muted-foreground"
            : "bg-gradient-to-r from-neon to-neon-secondary text-primary-foreground hover:shadow-[0_0_40px_-5px_rgba(0,255,170,0.4)]"
        )}
      >
        {isLoading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Analyzing</span>
            <span className="flex gap-1">
              <span className="animate-bounce" style={{ animationDelay: "0ms" }}>.</span>
              <span className="animate-bounce" style={{ animationDelay: "150ms" }}>.</span>
              <span className="animate-bounce" style={{ animationDelay: "300ms" }}>.</span>
            </span>
          </>
        ) : (
          <>
            <Sparkles className="w-5 h-5" />
            <span>Run Query</span>
            <ArrowRight className={cn(
              "w-5 h-5 transition-transform duration-300",
              !disabled && "group-hover:translate-x-1"
            )} />
          </>
        )}
      </button>
    </div>
  );
}
