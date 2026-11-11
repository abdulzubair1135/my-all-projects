import { useState, useEffect, useRef } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { CommunityMessage, User } from "@shared/schema";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { ArrowLeft, Send, Loader2, Users } from "lucide-react";
import { Link } from "wouter";
import { useAuth } from "@/hooks/use-auth";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { Sidebar, Topbar } from "@/components/Navigation";
import { format } from "date-fns";

export default function CommunityPage() {
  const { user } = useAuth();
  const [message, setMessage] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data: messages, isLoading } = useQuery<(CommunityMessage & { user: User })[]>({
    queryKey: ["/api/community"],
    refetchInterval: 3000, // Poll every 3 seconds for new messages
  });

  const sendMessage = useMutation({
    mutationFn: async () => {
      return apiRequest("POST", "/api/community", { content: message });
    },
    onSuccess: () => {
      setMessage("");
      queryClient.invalidateQueries({ queryKey: ["/api/community"] });
    }
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sortedMessages = [...(messages || [])].reverse();

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Topbar />
      <Sidebar />

      <main className="pt-24 lg:pl-72 pb-12 px-4 max-w-4xl mx-auto">
        <div className="flex items-center gap-4 mb-8">
          <Link href="/">
            <Button variant="ghost" size="icon" data-testid="button-back">
              <ArrowLeft className="w-5 h-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold">Community Chat</h1>
            <p className="text-muted-foreground text-sm">Chat with everyone on campus</p>
          </div>
        </div>

        <Card className="h-[calc(100vh-280px)] flex flex-col">
          <div className="p-4 border-b border-border flex items-center gap-2">
            <Users className="w-5 h-5 text-primary" />
            <span className="font-semibold">Campus Community</span>
            <span className="text-sm text-muted-foreground ml-auto">
              {messages?.length || 0} messages
            </span>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {isLoading ? (
              <div className="flex justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
              </div>
            ) : sortedMessages.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No messages yet. Start the conversation!</p>
              </div>
            ) : (
              sortedMessages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex gap-3 ${msg.userId === user?.id ? 'flex-row-reverse' : ''}`}
                >
                  <Link href={`/profile/${msg.user?.username}`}>
                    <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-lg cursor-pointer hover:ring-2 ring-primary/50 transition-all">
                      {msg.user?.profileEmoji || "🎓"}
                    </div>
                  </Link>
                  <div className={`max-w-[70%] ${msg.userId === user?.id ? 'text-right' : ''}`}>
                    <div className="flex items-center gap-2 mb-1">
                      <Link href={`/profile/${msg.user?.username}`}>
                        <span className="text-sm font-medium hover:underline cursor-pointer">
                          {msg.user?.username}
                        </span>
                      </Link>
                      <span className="text-xs text-muted-foreground">
                        {format(new Date(msg.createdAt!), "p")}
                      </span>
                    </div>
                    <div className={`p-3 rounded-2xl inline-block ${
                      msg.userId === user?.id 
                        ? 'bg-primary text-primary-foreground' 
                        : 'bg-secondary'
                    }`}>
                      <p className="text-sm">{msg.content}</p>
                    </div>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="p-4 border-t border-border flex gap-2">
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Say something to the community..."
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && message && sendMessage.mutate()}
              data-testid="input-community-message"
            />
            <Button 
              onClick={() => sendMessage.mutate()} 
              disabled={!message || sendMessage.isPending}
              data-testid="button-send-community"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </Card>
      </main>
    </div>
  );
}
