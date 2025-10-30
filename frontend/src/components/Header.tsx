import rumiLogo from "@/assets/rumi-logo.png";
import { BarChart3, LogOut } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

export const Header = () => {
  const { logout, username } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <header className="border-b border-border/40 backdrop-blur-xl bg-background/80 sticky top-0 z-50 shadow-sm transition-all duration-300">
      <div className="container mx-auto px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-3 group cursor-pointer">
          <img 
            src={rumiLogo} 
            alt="Rumi Logo" 
            className="h-10 w-10 object-contain transition-transform duration-300 group-hover:scale-110" 
          />
          <h1 className="text-2xl font-semibold tracking-tight bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text">
            Rumi
          </h1>
        </div>
        <div className="flex items-center gap-3">
          <div className="px-4 py-2 rounded-full bg-secondary/50 backdrop-blur-sm text-sm font-medium text-secondary-foreground shadow-sm hover:shadow-md transition-all duration-300 hover:bg-secondary/60">
            {username || "User"}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
            className="rounded-full hover:bg-destructive/10 hover:text-destructive transition-all duration-300 hover:scale-105"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </div>
    </header>
  );
};
