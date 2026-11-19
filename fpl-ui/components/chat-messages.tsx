"use client";

import { useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import { Bot, User, Sparkles, Zap, Clock, ChevronDown, ChevronUp } from "lucide-react";
import { type ModelResult } from "./latency-table";
import { type KnowledgeGraphResult } from "./knowledge-graph-panel";
import { useState } from "react";

export interface ChatMessage {
  id: string;
  type: "user" | "assistant";
  content: string;
  timestamp: Date;
  models?: string[];
  modelResults?: ModelResult[];
  knowledgeGraph?: KnowledgeGraphResult;
}

interface ChatMessagesProps {
  messages: ChatMessage[];
  isLoading?: boolean;
  className?: string;
}

function UserBubble({ message }: { message: ChatMessage }) {
  return (
    <div className="flex justify-end gap-3 animate-in slide-in-from-right-4 fade-in duration-300">
      <div className="flex flex-col items-end gap-2 max-w-[85%] lg:max-w-[75%]">
        <div className="flex items-center gap-2">
          {message.models && message.models.length > 0 && (
            <div className="flex items-center gap-1.5">
              {message.models.map((model) => (
                <span
                  key={model}
                  className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-neon/10 text-neon border border-neon/20"
                >
                  {model}
                </span>
              ))}
            </div>
          )}
          <span className="text-[10px] text-muted-foreground/50">
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
        <div className={cn(
          "rounded-2xl rounded-tr-md px-5 py-3.5",
          "bg-gradient-to-br from-neon/20 to-neon/10",
          "border border-neon/20",
          "shadow-[0_4px_20px_-4px_rgba(0,0,0,0.3)]"
        )}>
          <p className="text-sm text-foreground leading-relaxed">{message.content}</p>
        </div>
      </div>
      <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-gradient-to-br from-neon/20 to-neon/5 border border-neon/20 flex items-center justify-center">
        <User className="w-4 h-4 text-neon" />
      </div>
    </div>
  );
}

function AssistantBubble({ message }: { message: ChatMessage }) {
  const [showDetails, setShowDetails] = useState(false);
  
  return (
    <div className="flex gap-3 animate-in slide-in-from-left-4 fade-in duration-300">
      <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-gradient-to-br from-secondary to-secondary/50 border border-border/50 flex items-center justify-center">
        <Bot className="w-4 h-4 text-foreground/70" />
      </div>
      <div className="flex flex-col gap-2 max-w-[85%] lg:max-w-[75%]">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-foreground/70">FPL Assistant</span>
          <span className="w-1.5 h-1.5 rounded-full bg-neon" />
          <span className="text-[10px] text-muted-foreground/50">
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
        <div className={cn(
          "rounded-2xl rounded-tl-md px-5 py-4",
          "bg-gradient-to-br from-card/90 to-card/60 backdrop-blur-sm",
          "border border-border/40",
          "shadow-[0_4px_20px_-4px_rgba(0,0,0,0.3)]"
        )}>
          <div className="prose prose-invert prose-sm max-w-none">
            {message.content.split('\n\n').map((paragraph, i) => (
              <p key={i} className="text-sm text-foreground/90 leading-relaxed mb-3 last:mb-0">
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
          
          {/* Model Results Summary */}
          {message.modelResults && message.modelResults.length > 0 && (
            <div className="mt-4 pt-4 border-t border-border/30">
              <button
                onClick={() => setShowDetails(!showDetails)}
                className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors group"
              >
                <Zap className="w-3 h-3 text-neon" />
                <span>Model performance</span>
                {showDetails ? (
                  <ChevronUp className="w-3 h-3 transition-transform" />
                ) : (
                  <ChevronDown className="w-3 h-3 transition-transform" />
                )}
              </button>
              
              {showDetails && (
                <div className="mt-3 space-y-2 animate-in slide-in-from-top-2 fade-in duration-200">
                  {message.modelResults.map((result) => (
                    <div
                      key={result.modelId}
                      className="flex items-center justify-between py-2 px-3 rounded-lg bg-secondary/30"
                    >
                      <span className="text-xs font-medium text-foreground/80">{result.modelName}</span>
                      <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {result.latency.toFixed(0)}ms
                        </span>
                        <span>{result.answerLength} chars</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
        <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground/40">
          <Sparkles className="w-3 h-3" />
          <span>AI-powered analysis</span>
        </div>
      </div>
    </div>
  );
}

function LoadingBubble() {
  return (
    <div className="flex gap-3 animate-in slide-in-from-left-4 fade-in duration-300">
      <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-gradient-to-br from-secondary to-secondary/50 border border-border/50 flex items-center justify-center">
        <Bot className="w-4 h-4 text-foreground/70" />
      </div>
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-foreground/70">FPL Assistant</span>
          <span className="w-1.5 h-1.5 rounded-full bg-neon animate-pulse" />
        </div>
        <div className={cn(
          "rounded-2xl rounded-tl-md px-5 py-4",
          "bg-gradient-to-br from-card/90 to-card/60 backdrop-blur-sm",
          "border border-border/40",
          "shadow-[0_4px_20px_-4px_rgba(0,0,0,0.3)]"
        )}>
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              <span className="w-2 h-2 rounded-full bg-neon/60 animate-bounce [animation-delay:0ms]" />
              <span className="w-2 h-2 rounded-full bg-neon/60 animate-bounce [animation-delay:150ms]" />
              <span className="w-2 h-2 rounded-full bg-neon/60 animate-bounce [animation-delay:300ms]" />
            </div>
            <span className="text-xs text-muted-foreground ml-2">Analyzing your query...</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center animate-in fade-in duration-500">
      <div className="relative mb-6">
        <div className="absolute inset-0 bg-neon/10 rounded-3xl blur-2xl" />
        <div className="relative w-20 h-20 rounded-2xl bg-gradient-to-br from-card to-card/50 border border-border/50 flex items-center justify-center">
          <Bot className="w-10 h-10 text-muted-foreground/40" />
        </div>
      </div>
      <h3 className="text-lg font-medium text-foreground/80 mb-2">Start a conversation</h3>
      <p className="text-sm text-muted-foreground/60 max-w-sm leading-relaxed">
        Ask about player picks, transfer strategies, captain choices, or any FPL insights
      </p>
    </div>
  );
}

export function ChatMessages({ messages, isLoading, className }: ChatMessagesProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  if (messages.length === 0 && !isLoading) {
    return <EmptyState />;
  }

  return (
    <div className={cn("space-y-6", className)}>
      {messages.map((message) => (
        message.type === "user" ? (
          <UserBubble key={message.id} message={message} />
        ) : (
          <AssistantBubble key={message.id} message={message} />
        )
      ))}
      {isLoading && <LoadingBubble />}
      <div ref={messagesEndRef} />
    </div>
  );
}
