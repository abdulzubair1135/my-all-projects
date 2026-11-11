import { Moon, Sun, Palette } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useTheme } from "./ThemeProvider";

const colorThemes = [
  { id: "indigo", name: "Indigo", color: "bg-indigo-500" },
  { id: "emerald", name: "Emerald", color: "bg-emerald-500" },
  { id: "rose", name: "Rose", color: "bg-rose-500" },
  { id: "amber", name: "Amber", color: "bg-amber-500" },
] as const;

export function ThemeToggle() {
  const { theme, colorTheme, setTheme, setColorTheme } = useTheme();

  return (
    <div className="flex items-center gap-1">
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
        data-testid="button-theme-toggle"
      >
        {theme === "dark" ? (
          <Sun className="h-5 w-5" />
        ) : (
          <Moon className="h-5 w-5" />
        )}
      </Button>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" data-testid="button-color-theme">
            <Palette className="h-5 w-5" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuLabel>Color Theme</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {colorThemes.map((t) => (
            <DropdownMenuItem
              key={t.id}
              onClick={() => setColorTheme(t.id)}
              className="flex items-center gap-2"
            >
              <div className={`w-4 h-4 rounded-full ${t.color}`} />
              <span>{t.name}</span>
              {colorTheme === t.id && <span className="ml-auto">*</span>}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
