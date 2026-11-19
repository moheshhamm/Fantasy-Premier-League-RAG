"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { QueryInput } from "@/components/query-input";
import { ModelPicker, AVAILABLE_MODELS } from "@/components/model-picker";
import { RunButton } from "@/components/run-button";
import { ChatMessages, type ChatMessage } from "@/components/chat-messages";
import { LatencyTable, type ModelResult } from "@/components/latency-table";
import {
  KnowledgeGraphPanel,
  type KnowledgeGraphResult,
} from "@/components/knowledge-graph-panel";
import { HistorySidebar, type HistoryItem } from "@/components/history-sidebar";
import { Trophy, Sparkles, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";


export default function FPLAssistant() {
  const [query, setQuery] = useState("");
  const [selectedModels, setSelectedModels] = useState<string[]>(["llama"]);
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [lastKnowledgeGraph, setLastKnowledgeGraph] = useState<KnowledgeGraphResult | null>(null);
  const [lastModelResults, setLastModelResults] = useState<ModelResult[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Keyboard shortcut for focus
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        const textarea = document.querySelector("textarea");
        textarea?.focus();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleToggleModel = useCallback((modelId: string) => {
    setSelectedModels((prev) =>
      prev.includes(modelId)
        ? prev.filter((id) => id !== modelId)
        : [...prev, modelId]
    );
  }, []);

  const handleRunQuery = useCallback(async () => {
    if (!query.trim() || selectedModels.length === 0) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: "user",
      content: query.trim(),
      timestamp: new Date(),
      models: selectedModels.map(id => AVAILABLE_MODELS.find(m => m.id === id)?.name || id),
    };

    setMessages(prev => [...prev, userMessage]);
    setQuery("");
    setIsLoading(true);
    setShowAnalytics(false);

    try {
   const res = await fetch("http://localhost:8000/query", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    question: userMessage.content,
    models: selectedModels,
  }),
});

const data = await res.json();

// Convert backend model responses to UI format
const results: ModelResult[] = Object.entries(data.model_responses).map(
  ([modelId, r]: any) => ({
    modelId,
    modelName: modelId,
    latency: r.latency ?? null,
    answerLength: r.answer?.length ?? 0,
    status: "success",
  })
);

// Build assistant message
const assistantMessage: ChatMessage = {
  id: (Date.now() + 1).toString(),
  type: "assistant",
  content: data.final_answer,
  timestamp: new Date(),
  modelResults: results,
};

setMessages((prev) => [...prev, assistantMessage]);
setLastModelResults(results);

// Add to history
const historyItem: HistoryItem = {
  id: Date.now().toString(),
  query: userMessage.content,
  timestamp: new Date(),
  models: selectedModels,
};
setHistory((prev) => [historyItem, ...prev.slice(0, 19)]);
    } finally {
      setIsLoading(false);
    }
  }, [query, selectedModels]);

  const handleSelectHistory = useCallback((item: HistoryItem) => {
    setQuery(item.query);
    setSelectedModels(item.models);
    setSidebarOpen(false);
  }, []);

  const handleDeleteHistory = useCallback((id: string) => {
    setHistory((prev) => prev.filter((item) => item.id !== id));
  }, []);

  const handleClearHistory = useCallback(() => {
    setHistory([]);
  }, []);

  const handleClearChat = useCallback(() => {
    setMessages([]);
    setLastKnowledgeGraph(null);
    setLastModelResults([]);
    setShowAnalytics(false);
  }, []);

  return (
  <div className="min-h-screen bg-background flex overflow-hidden">    
    <div
  className={cn(
    "transition-all duration-300 ease-out",
    sidebarOpen ? "w-80" : "w-0"
  )}
>
  <HistorySidebar
    history={history}
    onSelect={handleSelectHistory}
    onDelete={handleDeleteHistory}
    onClear={handleClearHistory}
    isOpen={sidebarOpen}
    onToggle={() => setSidebarOpen(!sidebarOpen)}
  />
</div>

      <main className="flex-1 min-h-screen flex flex-col">
        {/* Ambient background effects */}
        <div className="fixed inset-0 pointer-events-none overflow-hidden">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-neon/5 rounded-full blur-[120px]" />
          <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-neon-secondary/5 rounded-full blur-[120px]" />
        </div>

        {/* Header */}
        <header className="relative border-b border-border/30 bg-card/30 backdrop-blur-md">
          <div className="max-w-4xl mx-auto px-6 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="relative">
                  <div className="absolute inset-0 bg-neon/20 rounded-xl blur-lg" />
                  <div className="relative w-11 h-11 rounded-xl bg-gradient-to-br from-neon/20 to-neon/5 border border-neon/20 flex items-center justify-center">
                    <Trophy className="w-5 h-5 text-neon" />
                  </div>
                </div>
                <div>
                  <h1 className="text-xl font-semibold text-foreground tracking-tight">
                    FPL AI Assistant
                  </h1>
                  <p className="text-xs text-muted-foreground">
                    Multi-model AI inference
                  </p>
                </div>
              </div>
              {messages.length > 0 && (
                <button
                  onClick={handleClearChat}
                  className="text-xs text-muted-foreground hover:text-foreground transition-colors px-3 py-1.5 rounded-lg hover:bg-secondary/50"
                >
                  Clear chat
                </button>
              )}
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <div 
          ref={chatContainerRef}
          className="flex-1 overflow-y-auto"
        >
          <div className="max-w-4xl mx-auto px-6 py-8">
            <ChatMessages messages={messages} isLoading={isLoading} />
          </div>
        </div>

        {/* Analytics Panel (Collapsible) */}
        {lastModelResults.length > 0 && (
          <div className="relative border-t border-border/30 bg-card/30 backdrop-blur-md">
            <div className="max-w-4xl mx-auto px-6 py-4">
              <button
                onClick={() => setShowAnalytics(!showAnalytics)}
                className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors mb-4"
              >
                <Sparkles className="w-4 h-4 text-neon" />
                <span className="font-medium">Analytics & Knowledge Graph</span>
                <ChevronDown className={cn(
                  "w-4 h-4 transition-transform",
                  showAnalytics && "rotate-180"
                )} />
              </button>
              {showAnalytics && (
              <div className="grid gap-4 lg:grid-cols-2 animate-in slide-in-from-bottom-4 fade-in duration-300">
                <LatencyTable results={lastModelResults} />
                <KnowledgeGraphPanel data={lastKnowledgeGraph} />
              </div>
              )}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="relative border-t border-border/30 bg-card/50 backdrop-blur-md">
          <div className="max-w-4xl mx-auto px-6 py-6">
            <div className="space-y-4">
              <QueryInput
                value={query}
                onChange={setQuery}
                disabled={isLoading}
                onSubmit={handleRunQuery}
              />
              
              <div className="flex flex-col sm:flex-row sm:items-end gap-4">
                <div className="flex-1">
                  <ModelPicker
                    selectedModels={selectedModels}
                    onToggle={handleToggleModel}
                    disabled={isLoading}
                  />
                </div>
                <RunButton
                  onClick={handleRunQuery}
                  isLoading={isLoading}
                  disabled={!query.trim() || selectedModels.length === 0}
                />
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
