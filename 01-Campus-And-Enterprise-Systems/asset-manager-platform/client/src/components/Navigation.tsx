import { Link, useLocation } from "wouter";
import { 
  Home, 
  MessageSquare, 
  BookOpen, 
  Calendar, 
  Smile, 
  TrendingUp, 
  LogOut,
  User as UserIcon,
  Search,
  Menu,
  Settings,
  Users,
  FileText,
  Mail,
  HelpCircle,
  Shield
} from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState, useEffect, useRef } from "react";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { ThemeToggle } from "@/components/ThemeToggle";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useQuery } from "@tanstack/react-query";
import { Badge } from "@/components/ui/badge";

const NAV_ITEMS = [
  { icon: Home, label: "Home", href: "/", category: null },
  { icon: TrendingUp, label: "Trending", href: "/?trending=true", category: null },
  { icon: MessageSquare, label: "General", href: "/?category=general", category: "general" },
  { icon: BookOpen, label: "Notes", href: "/?category=notes", category: "notes" },
  { icon: Calendar, label: "Events", href: "/events", category: null },
  { icon: Smile, label: "Memes", href: "/?category=memes", category: "memes" },
  { icon: UserIcon, label: "Confessions", href: "/?category=confession", category: "confession" },
  { icon: Users, label: "Community", href: "/community", category: null },
  { icon: Mail, label: "Messages", href: "/messages", category: null },
  { icon: Settings, label: "Settings", href: "/settings", category: null },
  { icon: HelpCircle, label: "Help", href: "/help", category: null },
];

type SearchType = "posts" | "people";

export function Sidebar() {
  const [location] = useLocation();
  const { user } = useAuth();
  const searchParams = new URLSearchParams(window.location.search);
  const currentCategory = searchParams.get("category");
  const isTrending = searchParams.get("trending") === "true";

  const { data: unreadData } = useQuery<{ count: number }>({
    queryKey: ["/api/messages/unread-count"],
    enabled: !!user,
    refetchInterval: 30000,
  });

  const unreadCount = unreadData?.count || 0;

  return (
    <div className="hidden lg:flex flex-col w-64 h-screen fixed left-0 top-0 glass-panel pt-20 px-4 pb-6 overflow-y-auto">
      <div className="flex-1 space-y-1">
        {NAV_ITEMS.map((item) => {
          const isActive = item.href === location + window.location.search || 
                           (item.category && currentCategory === item.category) ||
                           (item.href.includes('trending') && isTrending);

          const showBadge = item.label === "Messages" && unreadCount > 0;

          return (
            <Link key={item.label} href={item.href}>
              <button 
                className={`
                  w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200
                  ${isActive 
                    ? "bg-primary/20 text-primary shadow-lg shadow-primary/10 border border-primary/20" 
                    : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                  }
                `}
                data-testid={`nav-${item.label.toLowerCase()}`}
              >
                <item.icon className="w-5 h-5" />
                {item.label}
                {showBadge && (
                  <Badge variant="destructive" className="ml-auto text-xs px-1.5 py-0 min-w-[20px] text-center" data-testid="badge-unread-messages">
                    {unreadCount > 99 ? "99+" : unreadCount}
                  </Badge>
                )}
              </button>
            </Link>
          );
        })}
        
        {user?.role === "admin" && (
          <Link href="/admin">
            <button 
              className={`
                w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200
                ${location === "/admin"
                  ? "bg-destructive/20 text-destructive shadow-lg shadow-destructive/10 border border-destructive/20" 
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                }
              `}
              data-testid="nav-admin"
            >
              <Shield className="w-5 h-5" />
              Admin Panel
            </button>
          </Link>
        )}
      </div>
      
      <div className="pt-6 border-t border-border">
        <div className="px-4 py-4 rounded-xl bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/20">
          <h4 className="text-sm font-semibold text-primary mb-1">Campus Pro</h4>
          <p className="text-xs text-muted-foreground mb-3">Get access to premium study materials.</p>
          <Button size="sm" className="w-full text-xs">Upgrade</Button>
        </div>
      </div>
    </div>
  );
}

interface SearchResult {
  type: "post" | "user";
  id: number;
  title: string;
  subtitle: string;
}

export function Topbar() {
  const { user, logout } = useAuth();
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [searchType, setSearchType] = useState<SearchType>("posts");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [, navigate] = useLocation();
  const searchRef = useRef<HTMLDivElement>(null);

  const { data: unreadData } = useQuery<{ count: number }>({
    queryKey: ["/api/messages/unread-count"],
    enabled: !!user,
    refetchInterval: 30000,
  });

  const unreadCount = unreadData?.count || 0;

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setShowResults(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    const search = async () => {
      try {
        if (searchType === "posts") {
          const res = await fetch(`/api/posts?search=${encodeURIComponent(searchQuery)}`, { credentials: "include" });
          const posts = await res.json();
          setSearchResults(
            posts.slice(0, 5).map((p: any) => ({
              type: "post" as const,
              id: p.id,
              title: p.title || p.caption?.slice(0, 50) || "Untitled",
              subtitle: `by ${p.user?.username || "Anonymous"} - ${p.type}`,
            }))
          );
        } else {
          const res = await fetch(`/api/users/search?q=${encodeURIComponent(searchQuery)}`, { credentials: "include" });
          if (res.ok) {
            const users = await res.json();
            setSearchResults(
              users.slice(0, 5).map((u: any) => ({
                type: "user" as const,
                id: u.id,
                title: u.username,
                subtitle: u.name || u.bio || "Student",
              }))
            );
          } else {
            setSearchResults([]);
          }
        }
      } catch {
        setSearchResults([]);
      }
    };

    const debounce = setTimeout(search, 300);
    return () => clearTimeout(debounce);
  }, [searchQuery, searchType]);

  const handleResultClick = (result: SearchResult) => {
    setShowResults(false);
    setSearchQuery("");
    if (result.type === "post") {
      navigate(`/?postId=${result.id}`);
    } else {
      navigate(`/profile/${result.title}`);
    }
  };

  return (
    <header className="fixed top-0 left-0 right-0 h-16 glass-card z-50 px-4 lg:px-6 flex items-center justify-between border-b border-border">
      <div className="flex items-center gap-4">
        <Sheet open={isMobileOpen} onOpenChange={setIsMobileOpen}>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" className="lg:hidden text-muted-foreground" data-testid="button-mobile-menu">
              <Menu className="w-5 h-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-64 bg-card border-r border-border p-0">
             <div className="flex flex-col h-full pt-16 px-4 pb-6">
                <div className="flex-1 space-y-1">
                  {NAV_ITEMS.map((item) => {
                    const showBadge = item.label === "Messages" && unreadCount > 0;
                    return (
                      <Link key={item.label} href={item.href} onClick={() => setIsMobileOpen(false)}>
                        <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-muted-foreground hover:bg-secondary hover:text-foreground transition-all">
                          <item.icon className="w-5 h-5" />
                          {item.label}
                          {showBadge && (
                            <Badge variant="destructive" className="ml-auto text-xs px-1.5 py-0 min-w-[20px] text-center">
                              {unreadCount > 99 ? "99+" : unreadCount}
                            </Badge>
                          )}
                        </button>
                      </Link>
                    );
                  })}
                </div>
             </div>
          </SheetContent>
        </Sheet>
        
        <Link href="/">
          <div className="flex items-center gap-2 cursor-pointer">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-primary/70 flex items-center justify-center shadow-lg shadow-primary/20">
              <BookOpen className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="font-display font-bold text-lg tracking-tight hidden sm:block">Campus<span className="text-primary">Hub</span></span>
          </div>
        </Link>
      </div>

      <div className="flex-1 max-w-md mx-4 hidden md:block" ref={searchRef}>
        <div className="relative">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="absolute left-3 top-1/2 -translate-y-1/2 flex items-center gap-1 text-muted-foreground hover:text-foreground transition-colors z-10" data-testid="button-search-type">
                {searchType === "posts" ? <FileText className="w-4 h-4" /> : <Users className="w-4 h-4" />}
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start">
              <DropdownMenuItem onClick={() => setSearchType("posts")} className="gap-2">
                <FileText className="w-4 h-4" />
                Search Posts
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setSearchType("people")} className="gap-2">
                <Users className="w-4 h-4" />
                Search People
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <Input 
            placeholder={searchType === "posts" ? "Search posts, notes..." : "Search people..."}
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setShowResults(true);
            }}
            onFocus={() => searchQuery && setShowResults(true)}
            className="w-full pl-10 bg-secondary/50 border-border focus:bg-secondary focus:border-primary/50 rounded-full transition-all"
            data-testid="input-search"
          />
          
          {showResults && searchResults.length > 0 && (
            <div className="absolute top-full mt-2 w-full bg-card border border-border rounded-xl shadow-lg overflow-hidden z-50">
              {searchResults.map((result, i) => (
                <button
                  key={`${result.type}-${result.id}`}
                  onClick={() => handleResultClick(result)}
                  className="w-full px-4 py-3 text-left hover:bg-secondary transition-colors flex items-center gap-3 border-b border-border last:border-0"
                  data-testid={`search-result-${i}`}
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${result.type === "user" ? "bg-primary/20 text-primary" : "bg-secondary text-muted-foreground"}`}>
                    {result.type === "user" ? <UserIcon className="w-4 h-4" /> : <FileText className="w-4 h-4" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate text-foreground">{result.title}</p>
                    <p className="text-xs text-muted-foreground truncate">{result.subtitle}</p>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2">
        <ThemeToggle />
        
        {user ? (
          <>
            <Link href={`/profile/${user.username}`}>
              <div className="hidden sm:flex flex-col items-end cursor-pointer mr-2">
                <span className="text-sm font-medium leading-none">{user.username}</span>
                <span className="text-xs text-muted-foreground">Student</span>
              </div>
            </Link>
            <Button variant="ghost" size="icon" onClick={() => logout.mutate()} className="text-muted-foreground hover:text-destructive" data-testid="button-logout">
              <LogOut className="w-5 h-5" />
            </Button>
          </>
        ) : (
          <div className="flex items-center gap-2">
            <Link href="/login">
              <Button variant="ghost" size="sm" data-testid="button-login">Log in</Button>
            </Link>
            <Link href="/register">
              <Button size="sm" data-testid="button-register">Join Now</Button>
            </Link>
          </div>
        )}
      </div>
    </header>
  );
}
