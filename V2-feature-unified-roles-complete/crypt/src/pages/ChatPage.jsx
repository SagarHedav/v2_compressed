import * as React from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "../lib/utils";
import { Button } from "../components/ui/Button";
import { ChatInput } from "../components/ui/ChatInput";
import { MessageBubble } from "../components/ui/MessageBubble";
import { PageTransition } from "../components/ui/PageTransition";

import {
  ArrowLeft,
  MessageSquare,
  Plus,
  X,
  User,
  Search,
  MessageSquarePlus
} from "lucide-react";
import { MdSearch } from "react-icons/md";

const MOCK_MESSAGES = [
  {
    role: "assistant",
    content: "Hello! I am Asvix, your academic assistant. How can I help you today?",
    timestamp: "10:00 AM",
  },
];

const MOCK_HISTORY = [
  { id: 1, title: "Quantum Physics Basics" },
  { id: 2, title: "Calculus Derivatives" },
  { id: 3, title: "Organic Chemistry" },
];

export function ChatPage() {
  const { t } = useLanguage();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const urlMode = searchParams.get("mode");

  const user = JSON.parse(localStorage.getItem("user") || "null");
  const isTeacher = user?.role === "teacher";
  const isGuest = !user;

  const [messages, setMessages] = React.useState(MOCK_MESSAGES);
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);
  const [searchQuery, setSearchQuery] = React.useState("");
  const [isSearchActive, setIsSearchActive] = React.useState(false);

  const handleSend = (text) => {
    if (isGuest && messages.length >= 20) return;

    setMessages((prev) => [
      ...prev,
      { role: "user", content: text, timestamp: "Now" },
      { role: "assistant", content: "Here is the explanation for your question.", timestamp: "Now" },
    ]);
  };

  const filteredHistory = MOCK_HISTORY.filter((item) =>
    item.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  /* ================= SIDEBAR ================= */
  const SidebarContent = () => (
    <>
      {/* Header */}
      <div className="flex h-16 items-center justify-between border-b px-6">
        <Link to="/dashboard" className="flex items-center gap-2 text-sm text-muted-foreground">
          <ArrowLeft className="h-4 w-4" />
          Dashboard
        </Link>
        <button onClick={() => setIsSidebarOpen(false)}>
          <X className="h-5 w-5 text-muted-foreground" />
        </button>
      </div>

      {/* Actions */}
      <div className="px-4 py-4 space-y-2">
        <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm hover:bg-accent/10">
          <MessageSquarePlus className="h-4 w-4" />
          New Chat
        </button>

        <button
          onClick={() => setIsSearchActive(!isSearchActive)}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm hover:bg-accent/10"
        >
          <Search className="h-4 w-4" />
          Search Chat
        </button>

        {isSearchActive && (
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search history..."
            className="mt-2 w-full rounded-md border px-3 py-1.5 text-xs"
          />
        )}
      </div>

      {/* ===== IMPROVED CHAT HISTORY ===== */}
      <div className="flex-1 overflow-y-auto px-4 pb-4">
        {/* Section header */}
        <div className="mb-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Chat History
          </h3>
          <div className="mt-2 h-px bg-border" />
        </div>

        {/* History list */}
        <div className="space-y-1">
          {filteredHistory.length > 0 ? (
            filteredHistory.map((item) => (
              <button
                key={item.id}
                className="flex w-full items-center gap-3 rounded-md px-2 py-2 text-sm hover:bg-accent/10"
              >
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
                <span className="truncate">{item.title}</span>
              </button>
            ))
          ) : (
            <p className="text-xs text-muted-foreground py-4">
              No conversations found
            </p>
          )}
        </div>
      </div>

      {/* User */}
      <div
        onClick={() => navigate("/profile")}
        className="border-t px-4 py-4 flex items-center gap-3 cursor-pointer hover:bg-accent/10"
      >
        <div className="h-9 w-9 rounded-full bg-accent/20 flex items-center justify-center">
          <User className="h-4 w-4" />
        </div>
        <div className="truncate">
          <p className="text-sm font-medium">{user?.name || "Guest User"}</p>
          <p className="text-xs text-muted-foreground">{user?.role || "Visitor"}</p>
        </div>
      </div>
    </>
  );

  return (
    <PageTransition className="relative flex h-screen bg-background-base">
      <AnimatePresence>
        {isSidebarOpen && (
          <>
            <motion.div
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              className="fixed left-0 top-0 z-50 h-full w-80 bg-background-base border-r"
            >
              <SidebarContent />
            </motion.div>
            <div
              onClick={() => setIsSidebarOpen(false)}
              className="fixed inset-0 bg-black/40 z-40"
            />
          </>
        )}
      </AnimatePresence>

      {/* Chat */}
      <div className="flex flex-1 flex-col">
        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="mx-auto max-w-3xl space-y-6">
            {messages.map((msg, i) => (
              <MessageBubble key={i} message={msg} />
            ))}
          </div>
        </div>

        <div className="fixed bottom-0 w-full pb-6">
          <div className="mx-auto max-w-3xl px-4">
            <ChatInput onSend={handleSend} placeholder="Send a message…" />
          </div>
        </div>
      </div>

      {/* Plus button */}
      {!isSidebarOpen && (
        <Button
          size="icon"
          onClick={() => setIsSidebarOpen(true)}
          className="fixed bottom-24 left-4 h-12 w-12 rounded-full"
        >
          <Plus className="h-6 w-6" />
        </Button>
      )}
    </PageTransition>
  );
}
