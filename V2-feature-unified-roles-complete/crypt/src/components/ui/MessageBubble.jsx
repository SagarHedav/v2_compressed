import { cn } from "../../lib/utils";
import { MdPerson, MdSmartToy, MdVolumeUp } from "react-icons/md";
import { motion } from "framer-motion";
import { Button } from "./Button";

export function MessageBubble({ message, isLast }) {
    const isUser = message.role === "user";

    const handleSpeak = () => {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel(); // Stop current
            const utterance = new SpeechSynthesisUtterance(message.content);
            window.speechSynthesis.speak(utterance);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={cn("flex w-full space-x-4 group", isUser ? "justify-end" : "justify-start")}
        >
            {!isUser && (
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent/20 border border-accent/20">
                    <MdSmartToy size={24} className="text-accent" />
                </div>
            )}

            <div className={cn(
                "relative max-w-[80%] rounded-2xl px-5 py-3.5 text-sm leading-relaxed shadow-sm",
                isUser
                    ? "bg-accent text-white rounded-tr-sm"
                    : "bg-white border border-black/5 text-foreground rounded-tl-sm dark:bg-[#1a1a1f] dark:border-white/5"
            )}>
                {message.content}

                <div className="mt-2 flex items-center justify-between">
                    <span className={cn("text-[10px] opacity-60", isUser ? "text-accent-100" : "text-foreground-muted")}>
                        {message.timestamp}
                    </span>

                    {!isUser && (
                        <button
                            onClick={handleSpeak}
                            className="text-foreground-muted hover:text-accent transition-colors opacity-0 group-hover:opacity-100 focus:opacity-100 ml-2"
                            title="Read aloud"
                        >
                            <MdVolumeUp size={22} />
                        </button>
                    )}
                </div>
            </div>

            {isUser && (
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gray-100 border border-black/5 dark:bg-white/10 dark:border-white/10">
                    <MdPerson size={24} className="text-foreground" />
                </div>
            )}
        </motion.div>
    );
}
