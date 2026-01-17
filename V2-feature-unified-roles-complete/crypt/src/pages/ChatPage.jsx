import * as React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "../components/ui/Button";
import { ChatInput } from "../components/ui/ChatInput";
import { MessageBubble } from "../components/ui/MessageBubble";
import { PageTransition } from "../components/ui/PageTransition";
import { ArrowLeft } from "lucide-react";

/* =========================
   CONFIG
========================= */
const GUEST_CHAT_LIMIT = 10;

/* =========================
   INITIAL MESSAGE
========================= */
const MOCK_MESSAGES = [
  {
    role: "assistant",
    content:
      "Hello! I am Asvix, your academic assistant. How can I help you today?",
    timestamp: "10:00 AM",
  },
];

export function ChatPage() {
  const { t } = useLanguage();
  const navigate = useNavigate();

  const user = JSON.parse(localStorage.getItem("user") || "null");
  const isTeacher = user?.role === "teacher";
  const isGuest = !user;

  const [messages, setMessages] = React.useState(MOCK_MESSAGES);
  const [guestCount, setGuestCount] = React.useState(0);
  const [showAuthPopup, setShowAuthPopup] = React.useState(false);

  /* =========================
     SEND MESSAGE HANDLER
  ========================= */
  const handleSend = (text) => {
    // 🚫 HARD STOP (block 11th message)
    if (isGuest && guestCount >= GUEST_CHAT_LIMIT) {
      setShowAuthPopup(true);
      return;
    }

    // Count ONLY guest user prompts
    if (isGuest) {
      setGuestCount((prev) => prev + 1);
    }

    const userMsg = {
      role: "user",
      content: text,
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    setMessages((prev) => [...prev, userMsg]);

    // Mock AI response
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: isTeacher
            ? "I have analyzed the topic. Here is a suggested lesson plan structure."
            : "Here is the explanation for your question.",
          timestamp: new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          }),
        },
      ]);
    }, 1000);
  };

  /* =========================
     SHOW POPUP AT EXACT LIMIT
  ========================= */
  React.useEffect(() => {
    if (isGuest && guestCount === GUEST_CHAT_LIMIT) {
      setShowAuthPopup(true);
    }
  }, [guestCount, isGuest]);

  return (
    <PageTransition className="relative flex h-screen w-full overflow-hidden bg-background-base text-foreground">
      {/* Sidebar */}
      <div className="hidden w-80 flex-col border-r lg:flex">
        <div className="flex h-16 items-center px-6 border-b">
          <Link to="/dashboard" className="flex items-center space-x-2">
            <ArrowLeft className="h-4 w-4" />
            <span className="text-sm">{t("chat.backToDashboard")}</span>
          </Link>
        </div>
      </div>

      {/* Chat */}
      <div className="flex flex-1 flex-col">
        <div className="flex-1 overflow-y-auto p-6">
          <div className="mx-auto max-w-3xl space-y-6">
            {messages.map((msg, idx) => (
              <MessageBubble key={idx} message={msg} />
            ))}
            <div className="h-24" />
          </div>

          {/* Input */}
          <div className="fixed bottom-0 left-0 w-full pb-6 pt-10 lg:pl-80">
            <div className="mx-auto max-w-3xl px-4">
              <ChatInput
                onSend={handleSend}
                disabled={isGuest && guestCount >= GUEST_CHAT_LIMIT}
                placeholder={t("chat.inputPlaceholder")}
              />
            </div>
          </div>
        </div>
      </div>

      {/* AUTH POPUP */}
      <AnimatePresence>
        {showAuthPopup && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="bg-white dark:bg-[#1a1a1f] rounded-2xl p-6 w-full max-w-sm"
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
            >
              <h2 className="text-lg font-semibold text-center mb-2">
                Chat Limit Reached
              </h2>
              <p className="text-sm text-center mb-6">
                You’ve used all 10 free messages. Please sign in or sign up to
                continue.
              </p>

              <div className="flex gap-3">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => navigate("/login")}
                >
                  Sign In
                </Button>
                <Button
                  className="flex-1"
                  onClick={() => navigate("/signup")}
                >
                  Sign Up
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </PageTransition>
  );
}
