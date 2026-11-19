"use client";

import { cn } from "@/lib/utils";
import { Cpu, Check } from "lucide-react";

export interface Model {
  id: string;
  name: string;
  description: string;
  badge?: string;
}

export const AVAILABLE_MODELS: Model[] = [
  { id: "llama", name: "LLaMA 3.1", description: "Open-source", badge: "Fast" },
  { id: "qwen", name: "Qwen 2.5", description: "Balanced", badge: "New" },
  { id: "gpt-oss", name: "GPT-OSS", description: "Accurate" },
];

interface ModelPickerProps {
  selectedModels: string[];
  onToggle: (modelId: string) => void;
  disabled?: boolean;
}

export function ModelPicker({
  selectedModels,
  onToggle,
  disabled = false,
}: ModelPickerProps) {
  return (
    <div className="space-y-4">
      {/* Label */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-secondary/50 flex items-center justify-center">
          <Cpu className="w-4 h-4 text-muted-foreground" />
        </div>
        <div>
          <span className="text-sm font-medium text-foreground">Models</span>
          <span className="text-xs text-muted-foreground ml-2">
            {selectedModels.length} selected
          </span>
        </div>
      </div>

      {/* Pill buttons */}
      <div className="flex flex-wrap gap-3">
        {AVAILABLE_MODELS.map((model) => {
          const isSelected = selectedModels.includes(model.id);
          return (
            <button
              key={model.id}
              onClick={() => onToggle(model.id)}
              disabled={disabled}
              className={cn(
                "group relative flex items-center gap-3 px-5 py-3 rounded-full",
                "border transition-all duration-300",
                "hover:scale-[1.02] active:scale-[0.98]",
                isSelected
                  ? "bg-neon/10 border-neon/50 shadow-[0_0_20px_-5px_rgba(0,255,170,0.3)]"
                  : "bg-card/50 border-border/50 hover:border-border hover:bg-card",
                disabled && "opacity-50 cursor-not-allowed hover:scale-100"
              )}
            >
              {/* Checkbox indicator */}
              <div
                className={cn(
                  "w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all duration-200",
                  isSelected
                    ? "bg-neon border-neon"
                    : "border-muted-foreground/30 group-hover:border-muted-foreground/50"
                )}
              >
                <Check className={cn(
                  "w-3 h-3 text-primary-foreground transition-all duration-200",
                  isSelected ? "opacity-100 scale-100" : "opacity-0 scale-50"
                )} />
              </div>

              {/* Model info */}
              <div className="text-left">
                <div className="flex items-center gap-2">
                  <span className={cn(
                    "text-sm font-medium transition-colors duration-200",
                    isSelected ? "text-foreground" : "text-muted-foreground group-hover:text-foreground"
                  )}>
                    {model.name}
                  </span>
                  {model.badge && (
                    <span className={cn(
                      "px-1.5 py-0.5 rounded text-[10px] font-medium uppercase tracking-wider",
                      isSelected
                        ? "bg-neon/20 text-neon"
                        : "bg-secondary text-muted-foreground"
                    )}>
                      {model.badge}
                    </span>
                  )}
                </div>
                <span className="text-xs text-muted-foreground/70">
                  {model.description}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
