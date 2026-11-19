"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { ChevronDown, Network, Copy, Check, GitBranch, Database } from "lucide-react";

export interface KnowledgeGraphResult {
  nodes: Array<{ id: string; label: string; type: string }>;
  edges: Array<{ source: string; target: string; relation: string }>;
  rawData: object;
}

interface KnowledgeGraphPanelProps {
  data: KnowledgeGraphResult | null;
  className?: string;
}

export function KnowledgeGraphPanel({ data, className }: KnowledgeGraphPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!data) {
    return null;
  }

  const handleCopy = async () => {
    await navigator.clipboard.writeText(JSON.stringify(data.rawData, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={cn(
        "rounded-2xl overflow-hidden",
        "bg-gradient-to-br from-card/80 to-card/40 backdrop-blur-sm",
        "border border-border/30",
        className
      )}
    >
      {/* Toggle Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-6 py-4 hover:bg-secondary/20 transition-colors duration-150"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-secondary/50 flex items-center justify-center">
            <Network className="w-4 h-4 text-neon-secondary" />
          </div>
          <div className="text-left">
            <span className="text-sm font-medium text-foreground">Knowledge Graph</span>
            <span className="text-xs text-muted-foreground ml-2">
              {data.nodes.length} entities, {data.edges.length} relations
            </span>
          </div>
        </div>
        <ChevronDown
          className={cn(
            "w-5 h-5 text-muted-foreground transition-transform duration-300",
            isExpanded && "rotate-180"
          )}
        />
      </button>

      {/* Expandable Content */}
      <div
        className={cn(
          "overflow-hidden transition-all duration-300 ease-in-out",
          isExpanded ? "max-h-[700px] opacity-100" : "max-h-0 opacity-0"
        )}
      >
        <div className="px-6 pb-6 space-y-6">
          {/* Entity & Relations Grid */}
          <div className="grid md:grid-cols-2 gap-4">
            {/* Entities */}
            <div className="rounded-xl bg-secondary/20 border border-border/20 p-4">
              <div className="flex items-center gap-2 mb-4">
                <Database className="w-4 h-4 text-muted-foreground" />
                <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Entities
                </h4>
              </div>
              <div className="flex flex-wrap gap-2">
                {data.nodes.map((node) => (
                  <span
                    key={node.id}
                    className={cn(
                      "px-3 py-1.5 rounded-lg text-xs font-medium transition-colors duration-150",
                      node.type === "player" &&
                        "bg-neon/10 text-neon border border-neon/20",
                      node.type === "team" &&
                        "bg-neon-secondary/10 text-neon-secondary border border-neon-secondary/20",
                      node.type === "stat" &&
                        "bg-chart-5/10 text-chart-5 border border-chart-5/20",
                      !["player", "team", "stat"].includes(node.type) &&
                        "bg-secondary/50 text-muted-foreground border border-border/20"
                    )}
                  >
                    {node.label}
                  </span>
                ))}
              </div>
            </div>

            {/* Relations */}
            <div className="rounded-xl bg-secondary/20 border border-border/20 p-4">
              <div className="flex items-center gap-2 mb-4">
                <GitBranch className="w-4 h-4 text-muted-foreground" />
                <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Relations
                </h4>
              </div>
              <div className="space-y-2">
                {data.edges.slice(0, 5).map((edge, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-2 text-xs"
                  >
                    <span className="text-neon font-medium">{edge.source}</span>
                    <span className="px-2 py-0.5 rounded bg-secondary/50 text-muted-foreground">
                      {edge.relation}
                    </span>
                    <span className="text-neon-secondary font-medium">{edge.target}</span>
                  </div>
                ))}
                {data.edges.length > 5 && (
                  <span className="text-xs text-muted-foreground/60">
                    +{data.edges.length - 5} more relations
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Raw JSON */}
          <div className="rounded-xl bg-background/50 border border-border/20 overflow-hidden">
            <div className="flex items-center justify-between px-4 py-3 border-b border-border/20">
              <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Raw Response
              </h4>
              <button
                onClick={handleCopy}
                className={cn(
                  "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-150",
                  copied
                    ? "bg-neon/10 text-neon"
                    : "bg-secondary/50 text-muted-foreground hover:text-foreground hover:bg-secondary"
                )}
              >
                {copied ? (
                  <>
                    <Check className="w-3.5 h-3.5" />
                    Copied
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    Copy JSON
                  </>
                )}
              </button>
            </div>
            <pre className="p-4 overflow-auto max-h-48 text-xs font-mono text-muted-foreground/80 leading-relaxed">
              {JSON.stringify(data.rawData, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
