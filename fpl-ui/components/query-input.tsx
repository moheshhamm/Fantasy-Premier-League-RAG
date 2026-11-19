"use client";

import React from "react"

import { cn } from "@/lib/utils";
import { Search, Command } from "lucide-react";

interface QueryInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  onSubmit?: () => void;
}

export function QueryInput({
  value,
  onChange,
  placeholder = "Ask anything about FPL...",
  disabled = false,
  onSubmit,
}: QueryInputProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey && onSubmit) {
      e.preventDefault();
      onSubmit();
    }
  };
  return (
    <div className="relative group">
      {/* Ambient glow */}
      <div className="absolute -inset-1 bg-gradient-to-r from-neon/20 via-neon-secondary/20 to-neon/20 rounded-2xl blur-xl opacity-0 group-focus-within:opacity-60 transition-all duration-500" />
      
      {/* Main container */}
      <div
        className={cn(
          "relative flex items-start gap-4 p-5 rounded-2xl",
          "bg-card/80 backdrop-blur-sm",
          "border border-border/50",
          "shadow-[0_0_0_1px_rgba(255,255,255,0.03)]",
          "group-focus-within:border-neon/40",
          "group-focus-within:shadow-[0_0_40px_-10px_rgba(0,255,170,0.2)]",
          "transition-all duration-300",
          disabled && "opacity-50"
        )}
      >
        {/* Icon */}
        <div className="flex-shrink-0 mt-0.5">
          <div className={cn(
            "w-10 h-10 rounded-xl flex items-center justify-center",
            "bg-gradient-to-br from-neon/20 to-neon/5",
            "border border-neon/20",
            "transition-all duration-300",
            "group-focus-within:from-neon/30 group-focus-within:to-neon/10",
            "group-focus-within:border-neon/40"
          )}>
            <Search className="w-5 h-5 text-neon" />
          </div>
        </div>

        {/* Input area */}
        <div className="flex-1 min-w-0">
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={2}
            className={cn(
              "w-full bg-transparent text-foreground placeholder:text-muted-foreground/60",
              "text-lg leading-relaxed resize-none",
              "focus:outline-none",
              "disabled:cursor-not-allowed"
            )}
          />
          
          {/* Keyboard hints */}
          <div className="flex items-center gap-4 mt-3 pt-3 border-t border-border/30">
            <div className="flex items-center gap-2">
              <kbd className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-secondary/50 text-muted-foreground text-xs font-mono">
                <Command className="w-3 h-3" />
                <span>K</span>
              </kbd>
              <span className="text-xs text-muted-foreground/60">to focus</span>
            </div>
            <div className="flex items-center gap-2">
              <kbd className="inline-flex items-center px-2 py-1 rounded-md bg-secondary/50 text-muted-foreground text-xs font-mono">
                Enter
              </kbd>
              <span className="text-xs text-muted-foreground/60">to send</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
