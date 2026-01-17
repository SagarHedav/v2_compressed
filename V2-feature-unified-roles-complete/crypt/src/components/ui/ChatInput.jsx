import * as React from "react";
import { Button } from "./Button";
import { cn } from "../../lib/utils";
import { MdSend, MdAttachFile, MdMic, MdMicOff } from "react-icons/md";

export const ChatInput = React.forwardRef(({ className, onSend, disabled, ...props }, ref) => {
    const [value, setValue] = React.useState("");
    const [isListening, setIsListening] = React.useState(false);
    const textareaRef = React.useRef(null);
    const recognitionRef = React.useRef(null);

    React.useEffect(() => {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = true;
            recognitionRef.current.interimResults = true;

            recognitionRef.current.onresult = (event) => {
                let finalTranscript = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    }
                }
                if (finalTranscript) {
                    setValue((prev) => prev + (prev ? " " : "") + finalTranscript);
                }
            };

            recognitionRef.current.onerror = (event) => {
                console.error("Speech recognition error", event.error);
                setIsListening(false);
            };

            recognitionRef.current.onend = () => {
                // Auto-restart if we didn't manually stop? No, manual toggle is better UX for this context.
                // setIsListening(false); 
            };
        }
    }, []);

    const toggleListening = () => {
        if (!recognitionRef.current) return;

        if (isListening) {
            recognitionRef.current.stop();
            setIsListening(false);
        } else {
            recognitionRef.current.start();
            setIsListening(true);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (value.trim() && onSend) {
            onSend(value);
            setValue("");
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    return (
        <form
            onSubmit={handleSubmit}
            className={cn(
                "relative flex items-end w-full p-3 rounded-3xl transition-all duration-300",
                // Light Mode
                "bg-white border border-black/10 shadow-[0_4px_20px_-4px_rgba(0,0,0,0.1)] focus-within:shadow-[0_4px_25px_-5px_rgba(94,106,210,0.15)] focus-within:border-accent/40",
                // Dark Mode
                "dark:bg-[#1a1a1f] dark:border-white/5 dark:shadow-none dark:focus-within:bg-[#202025] dark:focus-within:border-white/10",
                className
            )}
        >
            <Button type="button" variant="ghost" size="icon" className="h-12 w-12 mr-2 text-foreground-muted hover:text-foreground shrink-0 rounded-full">
                <MdAttachFile size={30} className="rotate-45" />
            </Button>

            <textarea
                ref={ref || textareaRef}
                value={value}
                onChange={(e) => setValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type a message..."
                rows={1}
                className="flex-1 w-full bg-transparent border-0 px-2 py-3 text-base text-foreground focus:ring-0 focus:outline-none focus-visible:ring-0 focus-visible:outline-none resize-none max-h-32 placeholder:text-gray-400 dark:placeholder:text-foreground-subtle"
                style={{ minHeight: "24px" }}
                disabled={disabled}
                {...props}
            />

            <div className="flex items-center space-x-2 ml-2 shrink-0">
                <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={toggleListening}
                    className={cn(
                        "h-12 w-12 rounded-full transition-all",
                        isListening
                            ? "bg-red-500/10 text-red-500 animate-pulse"
                            : "text-foreground-muted hover:text-foreground"
                    )}
                >
                    {isListening ? <MdMicOff size={30} /> : <MdMic size={30} />}
                </Button>

                <Button
                    type="submit"
                    disabled={!value.trim() || disabled}
                    size="icon"
                    className={cn(
                        "h-12 w-12 rounded-full transition-all",
                        value.trim()
                            ? "bg-accent hover:bg-accent-bright text-white shadow-lg shadow-accent/25"
                            : "bg-gray-100 text-gray-400 dark:bg-white/5 dark:text-foreground-muted"
                    )}
                >
                    <MdSend size={28} className="ml-1" />
                </Button>
            </div>
        </form>
    );
});

ChatInput.displayName = "ChatInput";
