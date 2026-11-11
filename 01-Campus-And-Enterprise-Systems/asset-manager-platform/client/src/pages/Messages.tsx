import { useState, useEffect, useRef } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Message, User } from "@shared/schema";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { ArrowLeft, Send, Loader2, AlertTriangle, Mail, MessageSquare, UserPlus } from "lucide-react";
import { Link } from "wouter";
import { useAuth } from "@/hooks/use-auth";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { Sidebar, Topbar } from "@/components/Navigation";
import { format } from "date-fns";

export default function MessagesPage() {
  const { user } = useAuth();
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [message, setMessage] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data: inbox, isLoading } = useQuery<(Message & { sender: User })[]>({
    queryKey: ["/api/messages"],
  });

  const { data: following } = useQuery<User[]>({
    queryKey: ["/api/users", user?.id, "following"],
    queryFn: async () => {
      if (!user?.id) return [];
      const res = await fetch(`/api/users/${user.id}/following`, { credentials: "include" });
      if (!res.ok) return [];
      return res.json();
    },
    enabled: !!user?.id,
  });

  const { data: conversation } = useQuery<Message[]>({
    queryKey: ["/api/messages", selectedUser?.id],
    queryFn: async () => {
      const res = await fetch(`/api/messages/${selectedUser?.id}`, { credentials: "include" });
      if (!res.ok) return [];
      return res.json();
    },
    enabled: !!selectedUser,
  });

  const sendMessage = useMutation({
    mutationFn: async () => {
      return apiRequest("POST", "/api/messages", {
        receiverId: selectedUser?.id,
        content: message
      });
    },
    onSuccess: () => {
      setMessage("");
      queryClient.invalidateQueries({ queryKey: ["/api/messages", selectedUser?.id] });
      queryClient.invalidateQueries({ queryKey: ["/api/messages"] });
    }
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversation]);

  const uniqueSenders = inbox?.reduce((acc, msg) => {
    const senderId = msg.senderId === user?.id ? msg.receiverId : msg.senderId;
    const sender = msg.senderId === user?.id ? null : msg.sender;
    if (sender && !acc.find(u => u.id === sender.id)) {
      acc.push(sender);
    }
    return acc;
  }, [] as User[]) || [];

  // Combine followed users with existing conversations
  const allContacts = [...uniqueSenders];
  following?.forEach(f => {
    if (!allContacts.find(c => c.id === f.id)) {
      allContacts.push(f);
    }
  });

  const warnings = inbox?.filter(m => m.type === "warning") || [];

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Topbar />
      <Sidebar />

      <main className="pt-24 lg:pl-72 pb-12 px-4 max-w-6xl mx-auto">
        <div className="flex items-center gap-4 mb-8">
          <Link href="/">
            <Button variant="ghost" size="icon" data-testid="button-back">
              <ArrowLeft className="w-5 h-5" />
            </Button>
          </Link>
          <h1 className="text-3xl font-bold">Messages</h1>
        </div>

        {warnings.length > 0 && (
          <div className="mb-6 space-y-2">
            {warnings.map(w => (
              <Card key={w.id} className="p-4 border-destructive bg-destructive/10">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-destructive mt-0.5" />
                  <div>
                    <p className="font-medium text-destructive">Warning from Admin</p>
                    <p className="text-sm text-muted-foreground">{w.content}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {format(new Date(w.createdAt!), "PPp")}
                    </p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        <div className="grid md:grid-cols-3 gap-6 h-[calc(100vh-250px)]">
          <Card className="p-4 overflow-y-auto">
            <h2 className="font-semibold mb-4 flex items-center gap-2">
              <Mail className="w-4 h-4" />
              Conversations
            </h2>
            {isLoading ? (
              <div className="flex justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin" />
              </div>
            ) : allContacts.length === 0 ? (
              <div className="text-center py-8">
                <UserPlus className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">Follow users to chat with them</p>
              </div>
            ) : (
              <div className="space-y-2">
                {allContacts.map(contact => {
                  const hasConversation = uniqueSenders.find(s => s.id === contact.id);
                  return (
                    <button
                      key={contact.id}
                      onClick={() => setSelectedUser(contact)}
                      className={`w-full p-3 rounded-lg text-left transition-colors flex items-center gap-3 ${
                        selectedUser?.id === contact.id ? 'bg-primary/20' : 'hover:bg-secondary'
                      }`}
                      data-testid={`conversation-${contact.id}`}
                    >
                      <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-lg">
                        {contact.profileEmoji || "🎓"}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{contact.username}</p>
                        <p className="text-xs text-muted-foreground truncate">
                          {hasConversation ? "Tap to chat" : "Start a conversation"}
                        </p>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </Card>

          <Card className="md:col-span-2 flex flex-col">
            {selectedUser ? (
              <>
                <div className="p-4 border-b border-border flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-lg">
                    {selectedUser.profileEmoji || "🎓"}
                  </div>
                  <div>
                    <p className="font-medium">{selectedUser.username}</p>
                    <p className="text-xs text-muted-foreground">{selectedUser.name || "Student"}</p>
                  </div>
                </div>

                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {conversation?.length === 0 ? (
                    <div className="text-center text-muted-foreground py-8">
                      <p>No messages yet. Say hi!</p>
                    </div>
                  ) : (
                    conversation?.map((msg) => (
                      <div
                        key={msg.id}
                        className={`flex ${msg.senderId === user?.id ? 'justify-end' : 'justify-start'}`}
                      >
                        <div className={`max-w-[70%] p-3 rounded-2xl ${
                          msg.senderId === user?.id 
                            ? 'bg-primary text-primary-foreground' 
                            : 'bg-secondary'
                        }`}>
                          <p className="text-sm">{msg.content}</p>
                          <p className="text-xs opacity-70 mt-1">
                            {format(new Date(msg.createdAt!), "p")}
                          </p>
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
                    placeholder="Type a message..."
                    onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && message && sendMessage.mutate()}
                    data-testid="input-message"
                  />
                  <Button 
                    onClick={() => sendMessage.mutate()} 
                    disabled={!message || sendMessage.isPending}
                    data-testid="button-send-message"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-muted-foreground">
                <div className="text-center">
                  <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Select a conversation to start messaging</p>
                </div>
              </div>
            )}
          </Card>
        </div>
      </main>
    </div>
  );
}
