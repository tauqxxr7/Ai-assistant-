"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { Brain, Database, Globe2, Send, ShieldCheck, Trash2 } from "lucide-react";
import { API_BASE, FinalAnswer } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type Message = {
  role: "user" | "assistant";
  content: string;
  final?: FinalAnswer;
};

type Memory = {
  id: number;
  key: string;
  value: string;
};

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Ask me about a current topic or a specific website. I will search, check robots.txt and sitemaps when a domain is involved, and cite what I can verify."
    }
  ]);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState("ready");
  const [isStreaming, setIsStreaming] = useState(false);
  const [memories, setMemories] = useState<Memory[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    void loadMemories();
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, status]);

  async function loadMemories() {
    try {
      const response = await fetch(`${API_BASE}/api/memories`);
      const payload = await response.json();
      setMemories(payload.memories ?? []);
    } catch {
      setMemories([]);
    }
  }

  async function deleteMemory(id: number) {
    await fetch(`${API_BASE}/api/memories/${id}`, { method: "DELETE" });
    await loadMemories();
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    const message = input.trim();
    if (!message || isStreaming) return;

    setInput("");
    setMessages((current) => [...current, { role: "user", content: message }, { role: "assistant", content: "" }]);
    setIsStreaming(true);
    setStatus("thinking");

    try {
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          history: messages.map(({ role, content }) => ({ role, content }))
        })
      });
      if (!response.body) throw new Error("No stream returned");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split("\n\n");
        buffer = events.pop() ?? "";
        for (const rawEvent of events) {
          const eventType = rawEvent.match(/^event: (.+)$/m)?.[1];
          const dataLine = rawEvent.match(/^data: (.+)$/m)?.[1];
          if (!eventType || !dataLine) continue;
          const data = JSON.parse(dataLine);
          if (eventType === "status") setStatus(data.label);
          if (eventType === "token") {
            setMessages((current) => {
              const next = [...current];
              next[next.length - 1] = { ...next[next.length - 1], content: next[next.length - 1].content + data.text };
              return next;
            });
          }
          if (eventType === "final") {
            setMessages((current) => {
              const next = [...current];
              next[next.length - 1] = { ...next[next.length - 1], final: data };
              return next;
            });
          }
        }
      }
      setStatus("ready");
      await loadMemories();
    } catch (error) {
      setStatus("error");
      setMessages((current) => {
        const next = [...current];
        next[next.length - 1] = {
          role: "assistant",
          content: error instanceof Error ? error.message : "The assistant failed to respond."
        };
        return next;
      });
    } finally {
      setIsStreaming(false);
    }
  }

  return (
    <main className="grid min-h-screen grid-cols-1 bg-background text-foreground lg:grid-cols-[1fr_340px]">
      <section className="flex min-h-screen flex-col">
        <header className="border-b border-border px-5 py-4">
          <div className="mx-auto flex max-w-4xl items-center justify-between">
            <div>
              <h1 className="text-lg font-semibold">Live AI Assistant</h1>
              <p className="text-sm text-muted-foreground">Web-verified, sitemap-aware, memory-enabled agent</p>
            </div>
            <div className="flex items-center gap-2 rounded-md border border-border px-3 py-2 text-sm text-muted-foreground">
              <Brain className="h-4 w-4 text-primary" />
              {status}
            </div>
          </div>
        </header>

        <div className="mx-auto flex w-full max-w-4xl flex-1 flex-col gap-4 px-5 py-6">
          <div className="flex-1 space-y-5">
            {messages.map((message, index) => (
              <article key={index} className={cn("flex", message.role === "user" ? "justify-end" : "justify-start")}>
                <div className={cn("max-w-[82%] rounded-lg border px-4 py-3", message.role === "user" ? "border-primary/40 bg-primary/15" : "border-border bg-muted/60")}>
                  <p className="whitespace-pre-wrap text-sm leading-6">{message.content}</p>
                  {message.final ? <VerificationPanel final={message.final} /> : null}
                </div>
              </article>
            ))}
            <div ref={scrollRef} />
          </div>

          <form onSubmit={submit} className="sticky bottom-0 flex gap-3 border-t border-border bg-background py-4">
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              rows={2}
              placeholder="Ask: What are the latest updates on openai.com?"
              className="min-h-12 flex-1 resize-none rounded-md border border-border bg-muted px-4 py-3 text-sm outline-none ring-primary/40 focus:ring-2"
            />
            <Button size="icon" disabled={isStreaming} aria-label="Send message">
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </div>
      </section>

      <aside className="border-l border-border bg-muted/40 p-5">
        <div className="mb-5 grid grid-cols-3 gap-2 text-center text-xs text-muted-foreground">
          <Signal icon={<Globe2 className="h-4 w-4" />} label="search" />
          <Signal icon={<ShieldCheck className="h-4 w-4" />} label="verify" />
          <Signal icon={<Database className="h-4 w-4" />} label="memory" />
        </div>
        <h2 className="mb-3 text-sm font-semibold">Memory</h2>
        <div className="space-y-2">
          {memories.length === 0 ? <p className="text-sm text-muted-foreground">No saved memories yet.</p> : null}
          {memories.map((memory) => (
            <div key={memory.id} className="rounded-md border border-border bg-background p-3">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-sm font-medium">{memory.key}</p>
                  <p className="mt-1 text-xs leading-5 text-muted-foreground">{memory.value}</p>
                </div>
                <Button variant="ghost" size="icon" onClick={() => void deleteMemory(memory.id)} aria-label="Delete memory">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </aside>
    </main>
  );
}

function Signal({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <div className="rounded-md border border-border bg-background px-2 py-3">
      <div className="mx-auto mb-1 flex h-6 w-6 items-center justify-center text-primary">{icon}</div>
      {label}
    </div>
  );
}

function VerificationPanel({ final }: { final: FinalAnswer }) {
  return (
    <div className="mt-4 border-t border-border pt-3 text-xs text-muted-foreground">
      <div className="mb-2 font-medium text-foreground">Confidence: {final.confidence}</div>
      {final.sources.length > 0 ? (
        <div className="space-y-1">
          <div className="font-medium text-foreground">Sources</div>
          {final.sources.map((source) => (
            <a key={source.url} href={source.url} target="_blank" rel="noreferrer" className="block break-words text-primary hover:underline">
              {source.title || source.url}
            </a>
          ))}
        </div>
      ) : null}
      <VerificationList title="Verified" items={final.what_was_verified} />
      <VerificationList title="Could not verify" items={final.what_could_not_be_verified} />
    </div>
  );
}

function VerificationList({ title, items }: { title: string; items: string[] }) {
  if (!items.length) return null;
  return (
    <div className="mt-3">
      <div className="font-medium text-foreground">{title}</div>
      <ul className="mt-1 list-disc space-y-1 pl-4">
        {items.map((item, index) => (
          <li key={`${item}-${index}`}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
