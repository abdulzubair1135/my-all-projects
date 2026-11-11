import { usePosts } from "@/hooks/use-posts";
import { Sidebar, Topbar } from "@/components/Navigation";
import { PostCard } from "@/components/PostCard";
import { PostComposer } from "@/components/PostComposer";
import { useLocation, Link } from "wouter";
import { Loader2, TrendingUp, Info, LogIn, Crown, ExternalLink } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Event, Ad } from "@shared/schema";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";


export default function Home() {
  const { user, isLoading: authLoading } = useAuth();
  const { toast } = useToast();
  const [location, params] = useLocation();
  const searchParams = new URLSearchParams(window.location.search);
  
  const category = searchParams.get("category") || undefined;
  const trending = searchParams.get("trending") === "true";
  
  const { data: posts, isLoading, error } = usePosts({ category, trending });
  
  const { data: events } = useQuery<Event[]>({
    queryKey: ["/api/events"],
    queryFn: async () => {
      const res = await fetch("/api/events", { credentials: "include" });
      if (!res.ok) return [];
      return res.json();
    },
    enabled: !!user,
  });

  const { data: ads } = useQuery<Ad[]>({
    queryKey: ["/api/ads"],
  });

  // Get trending posts (most liked posts from last 24 hours)
  const now = new Date();
  const dayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
  const trendingPosts = posts?.filter(p => p.createdAt && new Date(p.createdAt) > dayAgo)
    .sort((a, b) => b.likesCount - a.likesCount)
    .slice(0, 4) || [];

  // Get admin users from the search endpoint (filter by role on server)
  const { data: adminUsers } = useQuery<any[]>({
    queryKey: ["/api/users/search", "admin"],
    queryFn: async () => {
      const res = await fetch("/api/users/search?q=", { credentials: "include" });
      if (!res.ok) return [];
      const users = await res.json();
      // Filter for admin role on client since search doesn't filter by role
      return users.filter((u: any) => u.role === "admin");
    },
    enabled: !!user,
  });

  const sendSubscriptionRequest = useMutation({
    mutationFn: async () => {
      // Find the first admin user to message
      const admin = adminUsers?.[0];
      if (!admin) {
        throw new Error("No admin found");
      }
      return apiRequest("POST", "/api/messages", {
        receiverId: admin.id,
        content: `Hi! I'm interested in Campus Pro subscription. Username: ${user?.username}, Email: ${user?.email}. Please help me get started!`
      });
    },
    onSuccess: () => {
      toast({ title: "Subscription request sent!", description: "Admin will contact you soon." });
      queryClient.invalidateQueries({ queryKey: ["/api/messages"] });
    },
    onError: () => {
      toast({ title: "Could not send request", description: "Please try again later.", variant: "destructive" });
    }
  });

  // Show login prompt if not authenticated
  if (!authLoading && !user) {
    return (
      <div className="min-h-screen bg-background text-foreground">
        <Topbar />
        <div className="flex items-center justify-center min-h-[80vh] px-4">
          <Card className="p-8 max-w-md w-full text-center">
            <LogIn className="w-16 h-16 mx-auto mb-6 text-primary" />
            <h1 className="text-2xl font-bold mb-2">Welcome to Campus Hub</h1>
            <p className="text-muted-foreground mb-6">
              Sign in to see posts, connect with classmates, and join the campus community.
            </p>
            <div className="flex gap-3 justify-center">
              <Link href="/login">
                <Button data-testid="button-login-prompt">Sign In</Button>
              </Link>
              <Link href="/register">
                <Button variant="outline" data-testid="button-register-prompt">Create Account</Button>
              </Link>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  const upcomingEvents = events?.filter(e => new Date(e.date) >= new Date()).slice(0, 5) || [];

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Topbar />
      <Sidebar />
      
      <main className="pt-24 lg:pl-72 pb-12 px-4 max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Feed */}
        <div className="lg:col-span-2">
          {/* Stories/Events - Only show when events exist */}
          {upcomingEvents.length > 0 && (
            <div className="flex gap-4 mb-8 overflow-x-auto pb-4 scrollbar-hide">
              {upcomingEvents.map((event) => (
                <Link key={event.id} href="/events">
                  <div className="flex flex-col items-center gap-2 shrink-0 cursor-pointer group">
                    <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-primary to-primary/50 p-[2px] shadow-lg shadow-primary/20 group-hover:scale-105 transition-transform">
                      <div className="w-full h-full rounded-full bg-card border-2 border-background flex items-center justify-center text-2xl">
                        {event.title.charAt(0)}
                      </div>
                    </div>
                    <span className="text-xs text-muted-foreground group-hover:text-foreground transition-colors truncate max-w-16">
                      {event.title}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}

          <PostComposer />

          {isLoading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
          ) : error ? (
            <div className="text-center py-12 text-destructive">
              Failed to load posts. Please try again.
            </div>
          ) : posts?.length === 0 ? (
            <div className="text-center py-12 glass-card rounded-2xl">
              <p className="text-muted-foreground">No posts found. Be the first to share something!</p>
            </div>
          ) : (
            <div className="space-y-6">
              {posts?.map((post) => (
                <PostCard key={post.id} post={post} />
              ))}
            </div>
          )}
        </div>

        {/* Right Sidebar - Fixed position */}
        <div className="hidden lg:block">
          <div className="sticky top-24 space-y-6">
            {/* Ads Section */}
            {ads && ads.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-muted-foreground">Sponsored</h3>
                {ads.slice(0, 2).map((ad) => (
                  <Card 
                    key={ad.id} 
                    className="overflow-hidden hover-elevate transition-all cursor-pointer group"
                    onClick={() => ad.linkUrl && window.open(ad.linkUrl, "_blank")}
                    data-testid={`card-ad-${ad.id}`}
                  >
                    <div className="relative">
                      <img 
                        src={ad.imageUrl} 
                        alt={ad.title} 
                        className="w-full h-32 object-cover"
                      />
                      {ad.linkUrl && (
                        <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <ExternalLink className="w-4 h-4 text-white drop-shadow-lg" />
                        </div>
                      )}
                    </div>
                    <div className="p-2">
                      <p className="text-xs font-medium truncate">{ad.title}</p>
                    </div>
                  </Card>
                ))}
              </div>
            )}

            {/* Trending Posts */}
            <div className="glass-card rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-4 text-primary">
                <TrendingUp className="w-5 h-5" />
                <h3 className="font-bold">Trending Now</h3>
              </div>
              <div className="space-y-4">
                {trendingPosts.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No trending posts yet</p>
                ) : (
                  trendingPosts.map((post) => (
                    <Link key={post.id} href={`/post/${post.id}`}>
                      <div className="cursor-pointer group">
                        <p className="text-sm font-medium group-hover:text-primary transition-colors line-clamp-2">
                          {post.content}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {post.likesCount} likes • @{post.user?.username || "anonymous"}
                        </p>
                      </div>
                    </Link>
                  ))
                )}
              </div>
            </div>

            {/* Campus Pro Subscription */}
            <div className="glass-card rounded-2xl p-6 bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/20">
              <div className="flex items-center gap-2 mb-3">
                <Crown className="w-5 h-5 text-primary" />
                <h3 className="font-bold text-primary">Campus Pro</h3>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                Get verified badge, priority support, and exclusive features.
              </p>
              <Button 
                size="sm" 
                className="w-full"
                onClick={() => sendSubscriptionRequest.mutate()}
                disabled={sendSubscriptionRequest.isPending}
                data-testid="button-campus-pro"
              >
                {sendSubscriptionRequest.isPending ? "Sending..." : "Get Campus Pro"}
              </Button>
            </div>

            {/* Community Rules */}
            <div className="glass-card rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-4 text-green-500">
                <Info className="w-5 h-5" />
                <h3 className="font-bold">Community Rules</h3>
              </div>
              <ul className="space-y-2 text-sm text-muted-foreground list-disc pl-4">
                <li>Be respectful to others.</li>
                <li>No hate speech or bullying.</li>
                <li>Keep confessions anonymous.</li>
                <li>Report inappropriate content.</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
