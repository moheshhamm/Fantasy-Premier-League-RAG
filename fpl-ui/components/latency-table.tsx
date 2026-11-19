"use client";

import { cn } from "@/lib/utils";
import { BarChart3, Zap, Clock, FileText, CheckCircle2 } from "lucide-react";

export interface ModelResult {
  modelId: string;
  modelName: string;
  latency: number;
  answerLength: number;
  status: "success" | "error" | "pending";
}

interface LatencyTableProps {
  results: ModelResult[];
  className?: string;
}

export function LatencyTable({ results, className }: LatencyTableProps) {
  if (results.length === 0) {
    return null;
  }

  const fastestLatency = Math.min(
    ...results.filter((r) => r.status === "success").map((r) => r.latency)
  );

  return (
    <div
      className={cn(
        "rounded-2xl overflow-hidden",
        "bg-gradient-to-br from-card/80 to-card/40 backdrop-blur-sm",
        "border border-border/30",
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center gap-3 px-6 py-4 border-b border-border/30 bg-secondary/20">
        <div className="w-8 h-8 rounded-lg bg-secondary/50 flex items-center justify-center">
          <BarChart3 className="w-4 h-4 text-neon" />
        </div>
        <span className="text-sm font-medium text-foreground">Model Performance</span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border/20">
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Model
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                <div className="flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5" />
                  Latency
                </div>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                <div className="flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5" />
                  Length
                </div>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/10">
            {results.map((result, index) => {
              const isFastest = result.latency === fastestLatency && result.status === "success";
              return (
                <tr
                  key={result.modelId}
                  className="hover:bg-secondary/20 transition-colors duration-150"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <span className="font-medium text-foreground">
                        {result.modelName}
                      </span>
                      {isFastest && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-neon/10 text-neon text-xs font-medium">
                          <Zap className="w-3 h-3" />
                          Fastest
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={cn(
                        "font-mono text-sm",
                        isFastest ? "text-neon" : "text-foreground/80"
                      )}
                    >
                      {result.latency.toFixed(0)}
                      <span className="text-muted-foreground ml-0.5">ms</span>
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-mono text-sm text-foreground/80">
                      {result.answerLength.toLocaleString()}
                      <span className="text-muted-foreground ml-1">chars</span>
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={cn(
                        "inline-flex items-center gap-1.5 text-xs font-medium",
                        result.status === "success"
                          ? "text-neon"
                          : result.status === "error"
                            ? "text-destructive"
                            : "text-muted-foreground"
                      )}
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      {result.status === "success"
                        ? "Complete"
                        : result.status === "error"
                          ? "Failed"
                          : "Pending"}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
