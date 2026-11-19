"use client";

import { cn } from "@/lib/utils";
import { Sparkles, MessageSquare, Bot } from "lucide-react";

interface AnswerPanelProps {
  answer: string | null;
  selectedModel?: string;
  className?: string;
}

export function AnswerPanel({ answer, selectedModel, className }: AnswerPanelProps) {
  if (!answer) {
    return (
      <div className={cn(
        "rounded-2xl p-12",
        "bg-gradient-to-br from-card/80 to-card/40 backdrop-blur-sm",
        "border border-border/30",
        "flex flex-col items-center justify-center min-h-72 text-center",
        className
      )}>
        <div className="relative mb-6">
          <div className="w-20 h-20 rounded-2xl bg-secondary/30 flex items-center justify-center">
            <MessageSquare className="w-10 h-10 text-muted-foreground/50" />
          </div>
          <div className="absolute -bottom-1 -right-1 w-8 h-8 rounded-lg bg-card border border-border flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-neon/50" />
          </div>
        </div>
        <h3 className="text-xl font-medium text-foreground/80 mb-2">Ready to assist</h3>
        <p className="text-sm text-muted-foreground/60 max-w-sm leading-relaxed">
          Ask about player picks, transfer strategies, captain choices, or any FPL insights
        </p>
      </div>
    );
  }

  return (
    <div className={cn(
      "rounded-2xl overflow-hidden",
      "bg-gradient-to-br from-card/80 to-card/40 backdrop-blur-sm",
      "border border-border/30",
      "shadow-[0_8px_32px_-8px_rgba(0,0,0,0.3)]",
      className
    )}>
      {/* Header */}
      <div className="flex items-center gap-4 px-6 py-4 border-b border-border/30 bg-secondary/20">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-neon/20 to-neon/5 border border-neon/20 flex items-center justify-center">
          <Bot className="w-5 h-5 text-neon" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-foreground">FPL Assistant</span>
            <span className="w-2 h-2 rounded-full bg-neon animate-pulse" />
          </div>
          {selectedModel && (
            <span className="text-xs text-muted-foreground">
              Powered by {selectedModel}
            </span>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        <div className="prose prose-invert prose-sm max-w-none">
          {answer.split('\n\n').map((paragraph, i) => (
            <p key={i} className="text-foreground/90 leading-relaxed mb-4 last:mb-0">
              {paragraph.split('**').map((text, j) => 
                j % 2 === 1 ? (
                  <strong key={j} className="text-foreground font-semibold">{text}</strong>
                ) : (
                  <span key={j}>{text}</span>
                )
              )}
            </p>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between px-6 py-3 border-t border-border/20 bg-secondary/10">
        <span className="text-xs text-muted-foreground/60">
          Generated just now
        </span>
        <div className="flex items-center gap-1 text-xs text-muted-foreground/60">
          <Sparkles className="w-3 h-3" />
          <span>AI-powered analysis</span>
        </div>
      </div>
    </div>
  );
}
