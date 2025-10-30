import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send } from "lucide-react";
import unicornTyping from "@/assets/unicorn-typing.png";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export const ChatInput = ({ onSend, disabled }: ChatInputProps) => {
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput("");
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    setIsTyping(e.target.value.length > 0);
  };

  return (
    <form onSubmit={handleSubmit} className="p-6 border-t border-border/40 bg-background/50 backdrop-blur-xl">
      <div className="container mx-auto max-w-4xl">
        <div className="flex gap-3 items-end">
          {isTyping && !disabled && (
            <div className="flex flex-col items-center gap-1 animate-in fade-in-50 slide-in-from-left-2">
              <img 
                src={unicornTyping} 
                alt="Typing" 
                className="w-16 h-16 rounded-full object-cover shadow-md"
              />
              <span className="text-[11px] font-medium text-muted-foreground">Typing...</span>
            </div>
          )}
          <Textarea
            value={input}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything..."
            disabled={disabled}
            className="min-h-[52px] max-h-[200px] resize-none rounded-[20px] px-5 py-3.5 text-[15px] shadow-sm border-border/50 focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all duration-300 hover:shadow-md"
            rows={1}
          />
          <Button
            type="submit"
            disabled={!input.trim() || disabled}
            size="icon"
            className="h-[52px] w-[52px] rounded-full shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 bg-primary hover:bg-primary/90"
          >
            <Send className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </form>
  );
};
