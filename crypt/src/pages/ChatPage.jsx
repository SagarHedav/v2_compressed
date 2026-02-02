import * as React from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import { motion, AnimatePresence } from "framer-motion";
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
    MessageSquarePlus,
} from "lucide-react";

/* =========================
   INITIAL DATA
========================= */
const INITIAL_MESSAGES = [
    {
        role: "assistant",
        content:
            "Hello! I am Asvix, your academic assistant. How can I help you today?",
        timestamp: "Now",
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

    const user = JSON.parse(localStorage.getItem("user") || "null");
    const isGuest = !user;

    const [messages, setMessages] = React.useState(INITIAL_MESSAGES);
    const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);
    const [searchQuery, setSearchQuery] = React.useState("");
    const [isSearchActive, setIsSearchActive] = React.useState(false);

    /* ================= SEND ================= */
    const handleSend = (text) => {
        if (isGuest && messages.length >= 20) return;

        setMessages((prev) => [
            ...prev,
            { role: "user", content: text, timestamp: "Now" },
            {
                role: "assistant",
                content: "Here is the explanation for your question.",
                timestamp: "Now",
            },
        ]);
    };

    /* ================= NEW CHAT ================= */
    const handleNewChat = () => {
        setMessages(INITIAL_MESSAGES);
        setSearchQuery("");
        setIsSearchActive(false);
        setIsSidebarOpen(false);
    };

    const filteredHistory = MOCK_HISTORY.filter((item) =>
        item.title.toLowerCase().includes(searchQuery.toLowerCase())
    );

    /* ================= SIDEBAR ================= */
    const SidebarContent = () => (
        <div className="flex h-full flex-col">
            <div className="flex h-16 items-center justify-between border-b px-6">
                <Link
                    to="/dashboard"
                    className="flex items-center gap-2 text-sm text-muted-foreground"
                >
                    <ArrowLeft className="h-4 w-4" />
                    Dashboard
                </Link>
                <button onClick={() => setIsSidebarOpen(false)}>
                    <X className="h-5 w-5 text-muted-foreground" />
                </button>
            </div>

            <div className="px-4 py-4 space-y-2">
                <button
                    onClick={handleNewChat}
                    className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm hover:bg-accent/10"
                >
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

            <div className="flex-1 overflow-y-auto px-4 pb-4">
                <h3 className="mb-2 text-xs font-semibold uppercase text-muted-foreground">
                    Chat History
                </h3>
                <div className="space-y-1">
                    {filteredHistory.map((item) => (
                        <button
                            key={item.id}
                            className="flex w-full items-center gap-3 rounded-md px-2 py-2 text-sm hover:bg-accent/10"
                        >
                            <MessageSquare className="h-4 w-4 text-muted-foreground" />
                            <span className="truncate">{item.title}</span>
                        </button>
                    ))}
                </div>
            </div>

            <div
                onClick={() => navigate("/profile")}
                className="border-t px-4 py-4 flex items-center gap-3 cursor-pointer hover:bg-accent/10"
            >
                <div className="h-9 w-9 rounded-full bg-accent/20 flex items-center justify-center">
                    <User className="h-4 w-4" />
                </div>
                <div>
                    <p className="text-sm font-medium">{user?.name || "Guest User"}</p>
                    <p className="text-xs text-muted-foreground">
                        {user?.role || "Visitor"}
                    </p>
                </div>
            </div>
        </div>
    );

    /* ================= MAIN ================= */
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

            {/* CHAT AREA */}
            <div className="flex flex-1 flex-col">
                <div className="flex-1 overflow-y-auto px-6 py-6">
                    <div className="mx-auto max-w-6xl space-y-3">
                        {messages.map((msg, i) => (
                            <div
                                key={i}
                                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"
                                    }`}
                            >
                                {/* 🔥 COMPACT CHATGPT SIZE */}
                                <div className="max-w-[48%] text-sm leading-relaxed">
                                    <MessageBubble message={msg} />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* INPUT */}
                <div className="fixed bottom-0 w-full border-t bg-background-base">
                    <div className="mx-auto max-w-6xl px-6 py-3">
                        <ChatInput onSend={handleSend} placeholder="Send a message…" />
                    </div>
                </div>
            </div>

            {!isSidebarOpen && (
                <Button
                    size="icon"
                    onClick={() => setIsSidebarOpen(true)}
                    className="fixed bottom-24 left-6 h-11 w-11 rounded-full"
                >
                    <Plus className="h-5 w-5" />
                </Button>
            )}
        </PageTransition>
    );
}