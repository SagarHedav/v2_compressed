import { useState } from "react";
import { cn } from "../../lib/utils";
import { MdPerson, MdSmartToy, MdVolumeUp, MdThumbUp, MdThumbDown } from "react-icons/md";
import { motion } from "framer-motion";

export function MessageBubble({ message }) {
    const isUser = message.role === "user";
    const [feedback, setFeedback] = useState(null);
    const [isHovered, setIsHovered] = useState(false);

    const handleSpeak = () => {
        if ("speechSynthesis" in window) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(message.content);
            window.speechSynthesis.speak(utterance);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            className={cn(
                "w-full flex",
                isUser ? "justify-end" : "justify-start"
            )}
        >
            {/* Message container with hover area */}
            <div
                className={cn(
                    "max-w-[75%] md:max-w-[60%]",
                    isUser ? "text-right" : "text-left"
                )}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
            >
                {/* ROLE LABEL */}
                <div className={cn(
                    "mb-1 flex items-center gap-2 text-xs text-foreground-muted",
                    isUser ? "justify-end" : "justify-start"
                )}>
                    {isUser ? (
                        <>
                            <MdPerson size={14} />
                            <span>You</span>
                        </>
                    ) : (
                        <>
                            <MdSmartToy size={14} />
                            <span>DigiLab</span>
                        </>
                    )}
                </div>

                {/* MESSAGE BODY WITH SIDE ACTIONS */}
                <div className={cn(
                    "flex items-center gap-2",
                    isUser ? "flex-row-reverse" : "flex-row"
                )}>
                    {/* Message Bubble */}
                    <div
                        className={cn(
                            "rounded-xl px-4 py-3 text-[15px] leading-relaxed",
                            isUser
                                ? "bg-accent text-white rounded-br-md"
                                : "bg-white border border-black/5 text-foreground dark:bg-[#1a1a1f] dark:border-white/5 rounded-bl-md"
                        )}
                    >
                        {message.content}
                    </div>

                    {/* Side Action Buttons - Only for bot messages, show on hover */}
                    {!isUser && (
                        <div
                            className={cn(
                                "flex items-center gap-1 transition-opacity duration-200",
                                isHovered || feedback ? "opacity-100" : "opacity-0"
                            )}
                        >
                            <button
                                onClick={() => setFeedback(feedback === 'like' ? null : 'like')}
                                className={cn(
                                    "p-1.5 rounded-full hover:bg-green-500/10 transition-colors",
                                    feedback === 'like' ? "text-green-500 bg-green-500/10" : "text-foreground-muted hover:text-green-500"
                                )}
                                title="Good response"
                            >
                                <MdThumbUp size={14} />
                            </button>
                            <button
                                onClick={() => setFeedback(feedback === 'dislike' ? null : 'dislike')}
                                className={cn(
                                    "p-1.5 rounded-full hover:bg-red-500/10 transition-colors",
                                    feedback === 'dislike' ? "text-red-500 bg-red-500/10" : "text-foreground-muted hover:text-red-500"
                                )}
                                title="Bad response"
                            >
                                <MdThumbDown size={14} />
                            </button>
                        </div>
                    )}
                </div>

                {/* FOOTER */}
                <div className={cn(
                    "mt-1 flex items-center text-[11px] text-foreground-muted",
                    isUser ? "justify-end" : "justify-start gap-4"
                )}>
                    <span>{message.timestamp}</span>

                    {!isUser && (
                        <button
                            onClick={handleSpeak}
                            className="flex items-center gap-1 hover:text-accent transition-colors"
                            title="Read aloud"
                        >
                            <MdVolumeUp size={14} />
                            <span>Read</span>
                        </button>
                    )}
                </div>
            </div>
        </motion.div>
    );
}
