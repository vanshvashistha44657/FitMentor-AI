"use client";

import { useEffect, useRef, useState } from "react";
import { Send } from "lucide-react";
import { useChatHistory, useSendChatMessage } from "@/hooks/useFitness";

interface Message {
  id: string;
  role: string;
  content: string;
  created_at: string;
}

export default function CoachChatPage() {
  const { data: history } = useChatHistory();
  const send = useSendChatMessage();
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, send.isPending]);

  const handleSend = () => {
    if (!input.trim()) return;
    send.mutate(input);
    setInput("");
  };

  return (
    <div className="flex flex-col h-[calc(100vh-5rem)]">
      <h1 className="font-display font-bold text-3xl mb-1">AI Coach</h1>
      <p className="text-mute mb-6">Ask about form, swaps, missed workouts — anything.</p>

      <div className="glass-panel flex-1 p-6 flex flex-col gap-4 overflow-y-auto">
        {(!history || history.length === 0) && (
          <p className="text-mute text-sm text-center mt-10">
            Start the conversation — try "I only have 20 minutes today" or "My shoulder hurts."
          </p>
        )}
        {history?.map((msg: Message) => (
          <div key={msg.id} className={`max-w-[75%] ${msg.role === "user" ? "self-end" : "self-start"}`}>
            <div
              className={`px-4 py-3 rounded-2xl text-sm ${
                msg.role === "user" ? "bg-ember-500 text-graphite-950" : "bg-white/5 text-bone border border-white/10"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {send.isPending && (
          <div className="self-start px-4 py-3 rounded-2xl text-sm bg-white/5 border border-white/10 text-mute">
            Coach is typing…
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="flex gap-3 mt-4">
        <input
          className="input-field flex-1"
          placeholder="Message your coach…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button onClick={handleSend} disabled={send.isPending} className="btn-primary px-4 disabled:opacity-60">
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}
