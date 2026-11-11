import { useState } from "react";
import { useRoute, Link, useLocation } from "wouter";
import { Sidebar, Topbar } from "@/components/Navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@shared/routes";
import { Loader2, Calendar, MapPin, Link as LinkIcon, Edit2, Heart, FileText, MessageSquare, UserPlus, UserCheck, Mail } from "lucide-react";
import { PostCard } from "@/components/PostCard";
import { User } from "@shared/schema";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";

type ProfileTab = "posts" | "likes" | "notes";

export default function Profile() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [, navigate] = useLocation();
  const [, params] = useRoute("/profile/:username");
  const username = params?.username;
  const [activeTab, setActiveTab] = useState<ProfileTab>("posts");

  const { data: profileUser } = useQuery<User>({
    queryKey: ["/api/users", username],
    queryFn: async () => {
      const res = await fetch(`/api/users/${username}`, { credentials: "include" });
      if (!res.ok) return null;
      return res.json();
    },
    enabled: !!username,
  });

  const { data: posts, isLoading } = useQuery({
    queryKey: [api.posts.list.path],
    queryFn: async () => {
      const res = await fetch(api.posts.list.path, { credentials: "include" });
      if (!res.ok) return [];
      return api.posts.list.responses[200].parse(await res.json());
    }
  });

  const { data: followCounts } = useQuery<{ followers: number; following: number }>({
    queryKey: ["/api/users", profileUser?.id, "follow-counts"],
    queryFn: async () => {
      const res = await fetch(`/api/users/${profileUser?.id}/follow-counts`, { credentials: "include" });
      if (!res.ok) return { followers: 0, following: 0 };
      return res.json();
    },
    enabled: !!profileUser?.id,
  });

  const { data: isFollowingData } = useQuery<{ isFollowing: boolean }>({
    queryKey: ["/api/users", profileUser?.id, "is-following"],
    queryFn: async () => {
      const res = await fetch(`/api/users/${profileUser?.id}/is-following`, { credentials: "include" });
      if (!res.ok) return { isFollowing: false };
      return res.json();
    },
    enabled: !!profileUser?.id && user?.id !== profileUser?.id,
  });

  const toggleFollow = useMutation({
    mutationFn: async () => {
      return apiRequest("POST", `/api/users/${profileUser?.id}/follow`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/users", profileUser?.id, "follow-counts"] });
      queryClient.invalidateQueries({ queryKey: ["/api/users", profileUser?.id, "is-following"] });
      toast({ title: isFollowingData?.isFollowing ? "Unfollowed" : "Following" });
    }
  });

  const userPosts = posts?.filter(p => p.user?.username === username) || [];
  const likedPosts = posts?.filter(p => p.hasLiked) || [];
  const notePosts = posts?.filter(p => p.user?.username === username && p.type === "notes") || [];

  const getDisplayPosts = () => {
    switch (activeTab) {
      case "posts":
        return userPosts;
      case "likes":
        return likedPosts;
      case "notes":
        return notePosts;
      default:
        return userPosts;
    }
  };

  const displayPosts = getDisplayPosts();
  const displayUser = profileUser || userPosts[0]?.user;
  const isOwnProfile = user?.username === username;

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Topbar />
      <Sidebar />

      <main className="pt-24 lg:pl-72 pb-12 px-4 max-w-5xl mx-auto">
        <div className="h-48 w-full rounded-2xl bg-gradient-to-r from-primary/80 to-primary/40 relative mb-12 overflow-hidden">
          <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-20" />
        </div>

        <div className="px-4 relative mb-8">
          <div className="absolute -top-16 left-4">
            <div className="w-32 h-32 rounded-full bg-card border-4 border-background flex items-center justify-center text-5xl font-bold text-primary shadow-xl">
              {displayUser?.profileEmoji || "🎓"}
            </div>
          </div>
          
          <div className="pt-16 pl-2 flex flex-wrap justify-between items-start gap-4">
            <div>
              <h1 className="text-3xl font-bold text-foreground mb-1">{displayUser?.name || username}</h1>
              <p className="text-muted-foreground text-sm mb-1">@{username}</p>
              <p className="text-muted-foreground mb-4">
                {displayUser?.bio || "Student at Campus Hub"}
              </p>
              
              <div className="flex gap-4 text-sm mb-4">
                <span><strong>{followCounts?.followers || 0}</strong> <span className="text-muted-foreground">Followers</span></span>
                <span><strong>{followCounts?.following || 0}</strong> <span className="text-muted-foreground">Following</span></span>
              </div>
            </div>
            
            <div className="flex gap-2">
              {isOwnProfile ? (
                <Link href="/settings">
                  <Button variant="outline" size="sm" className="gap-2" data-testid="button-edit-profile">
                    <Edit2 className="w-4 h-4" />
                    Edit Profile
                  </Button>
                </Link>
              ) : (
                <>
                  <Button 
                    variant={isFollowingData?.isFollowing ? "secondary" : "default"}
                    size="sm" 
                    className="gap-2"
                    onClick={() => toggleFollow.mutate()}
                    disabled={toggleFollow.isPending}
                    data-testid="button-follow"
                  >
                    {isFollowingData?.isFollowing ? (
                      <>
                        <UserCheck className="w-4 h-4" />
                        Following
                      </>
                    ) : (
                      <>
                        <UserPlus className="w-4 h-4" />
                        Follow
                      </>
                    )}
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="gap-2"
                    onClick={() => navigate("/messages")}
                    data-testid="button-message"
                  >
                    <Mail className="w-4 h-4" />
                    Message
                  </Button>
                </>
              )}
            </div>
          </div>
            
          <div className="flex flex-wrap gap-4 text-sm text-muted-foreground mb-6">
            <div className="flex items-center gap-1">
              <MapPin className="w-4 h-4" /> Campus
            </div>
            <div className="flex items-center gap-1">
              <LinkIcon className="w-4 h-4" /> github.com/{username}
            </div>
            <div className="flex items-center gap-1">
              <Calendar className="w-4 h-4" /> Joined {displayUser?.createdAt ? new Date(displayUser.createdAt).toLocaleDateString('en-US', { month: 'long', year: 'numeric' }) : 'Recently'}
            </div>
          </div>

          <div className="flex gap-6 border-b border-border pb-4 text-sm font-medium">
            <button 
              onClick={() => setActiveTab("posts")}
              className={`flex items-center gap-2 pb-4 -mb-4.5 transition-colors ${
                activeTab === "posts" 
                  ? "text-primary border-b-2 border-primary" 
                  : "text-muted-foreground hover:text-foreground"
              }`}
              data-testid="tab-posts"
            >
              <MessageSquare className="w-4 h-4" />
              Posts ({userPosts.length})
            </button>
            <button 
              onClick={() => setActiveTab("likes")}
              className={`flex items-center gap-2 pb-4 -mb-4.5 transition-colors ${
                activeTab === "likes" 
                  ? "text-primary border-b-2 border-primary" 
                  : "text-muted-foreground hover:text-foreground"
              }`}
              data-testid="tab-likes"
            >
              <Heart className="w-4 h-4" />
              Likes ({likedPosts.length})
            </button>
            <button 
              onClick={() => setActiveTab("notes")}
              className={`flex items-center gap-2 pb-4 -mb-4.5 transition-colors ${
                activeTab === "notes" 
                  ? "text-primary border-b-2 border-primary" 
                  : "text-muted-foreground hover:text-foreground"
              }`}
              data-testid="tab-notes"
            >
              <FileText className="w-4 h-4" />
              Notes ({notePosts.length})
            </button>
          </div>
        </div>

        <div className="space-y-6">
          {isLoading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
          ) : displayPosts.length === 0 ? (
            <div className="text-center py-12 glass-card rounded-2xl">
              <p className="text-muted-foreground">
                {activeTab === "posts" && "No posts yet."}
                {activeTab === "likes" && "No liked posts yet."}
                {activeTab === "notes" && "No notes shared yet."}
              </p>
            </div>
          ) : (
            displayPosts.map((post) => (
              <PostCard key={post.id} post={post} />
            ))
          )}
        </div>
      </main>
    </div>
  );
}
