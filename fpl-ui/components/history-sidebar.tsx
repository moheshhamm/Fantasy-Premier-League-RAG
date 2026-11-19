"use client";

import { cn } from "@/lib/utils";
import { History, Clock, Trash2, X, PanelLeftClose, PanelLeft } from "lucide-react";

export interface HistoryItem {
  id: string;
  query: string;
  timestamp: Date;
  models: string[];
}

interface HistorySidebarProps {
  history: HistoryItem[];
  onSelect: (item: HistoryItem) => void;
  onDelete: (id: string) => void;
  onClear: () => void;
  isOpen: boolean;
  onToggle: () => void;
}

export function HistorySidebar({
  history,
  onSelect,
  onDelete,
  onClear,
  isOpen,
  onToggle,
}: HistorySidebarProps) {
  return (
    <>
      {/* Toggle button (visible when closed on desktop) */}
      <button
        onClick={onToggle}
        className={cn(
          "fixed top-6 left-6 z-50 w-10 h-10 rounded-xl",
          "bg-card/80 backdrop-blur-sm border border-border/50",
          "flex items-center justify-center",
          "hover:bg-card hover:border-border transition-all duration-200",
          "shadow-[0_4px_12px_-2px_rgba(0,0,0,0.3)]",
          isOpen && "lg:hidden"
        )}
      >
        <PanelLeft className="w-5 h-5 text-muted-foreground" />
      </button>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40 lg:hidden"
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "h-full w-80",
          "bg-sidebar/95 backdrop-blur-md",
          "border-r border-sidebar-border/50",
          "flex flex-col",
          "transition-transform duration-300 ease-out",
          "lg:z-auto",
          "shadow-[4px_0_24px_-4px_rgba(0,0,0,0.3)]",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-5 border-b border-sidebar-border/50">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-neon/10 flex items-center justify-center">
              <History className="w-5 h-5 text-neon" />
            </div>
            <div>
              <h2 className="font-semibold text-sidebar-foreground">History</h2>
              <p className="text-xs text-muted-foreground">{history.length} queries</p>
            </div>
          </div>
          <div className="flex items-center gap-1">
            {history.length > 0 && (
              <button
                onClick={onClear}
                className="px-3 py-1.5 rounded-lg text-xs font-medium text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors duration-150"
              >
                Clear all
              </button>
            )}
            <button
              onClick={onToggle}
              className="w-8 h-8 rounded-lg flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-sidebar-accent transition-colors duration-150"
            >
              {isOpen ? (
                <PanelLeftClose className="w-4 h-4 lg:block hidden" />
              ) : (
                <PanelLeft className="w-4 h-4 lg:block hidden" />
              )}
              <X className="w-4 h-4 lg:hidden" />
            </button>
          </div>
        </div>

        {/* History List */}
        <div className="flex-1 overflow-y-auto py-3">
          {history.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
              <div className="w-14 h-14 rounded-2xl bg-sidebar-accent/50 flex items-center justify-center mb-4">
                <Clock className="w-7 h-7 text-muted-foreground/50" />
              </div>
              <p className="text-sm font-medium text-muted-foreground/80 mb-1">No history yet</p>
              <p className="text-xs text-muted-foreground/50 leading-relaxed">
                Your query history will appear here
              </p>
            </div>
          ) : (
            <div className="px-3 space-y-1">
              {history.map((item, index) => (
                <div
                  key={item.id}
                  className="group relative rounded-xl hover:bg-sidebar-accent/50 transition-all duration-150"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <button
                    onClick={() => onSelect(item)}
                    className="w-full text-left p-4 pr-12"
                  >
                    <p className="text-sm text-sidebar-foreground line-clamp-2 leading-relaxed mb-2">
                      {item.query}
                    </p>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-muted-foreground/60">
                        {item.timestamp.toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </span>
                      <span className="flex items-center gap-1 text-xs text-neon/70">
                        <span className="w-1.5 h-1.5 rounded-full bg-neon/50" />
                        {item.models.length} model{item.models.length !== 1 && "s"}
                      </span>
                    </div>
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(item.id);
                    }}
                    className="absolute right-3 top-1/2 -translate-y-1/2 w-8 h-8 rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-all duration-150"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-sidebar-border/30">
          <p className="text-xs text-muted-foreground/50 text-center">
            FPL AI Assistant v1.0
          </p>
        </div>
      </aside>
    </>
  );
}
