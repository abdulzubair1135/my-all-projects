import { useState, useRef } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { User, Report, Ad, Visitor, CollegeUser, PendingUser } from "@shared/schema";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { 
  Users, Flag, Image, AlertTriangle, Ban, CheckCircle, 
  Trash2, Send, ArrowLeft, Loader2, Plus, Crown, Eye, Shield, 
  AlertCircle, Globe, ImageIcon, UserPlus, GraduationCap, X, Check
} from "lucide-react";
import { Link, useLocation } from "wouter";
import { useAuth } from "@/hooks/use-auth";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Sidebar, Topbar } from "@/components/Navigation";
import { formatDistanceToNow } from "date-fns";

export default function AdminPage() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [, navigate] = useLocation();
  const [warningUserId, setWarningUserId] = useState<number | null>(null);
  const [warningMessage, setWarningMessage] = useState("");
  const [newAd, setNewAd] = useState({ title: "", linkUrl: "" });
  const [adImage, setAdImage] = useState<File | null>(null);
  const [adDialogOpen, setAdDialogOpen] = useState(false);
  const [emergencyDialogOpen, setEmergencyDialogOpen] = useState(false);
  const adFileInputRef = useRef<HTMLInputElement>(null);
  const [newCollegeUser, setNewCollegeUser] = useState({ username: "", email: "", name: "", department: "" });
  const [collegeUserDialogOpen, setCollegeUserDialogOpen] = useState(false);

  const { data: users, isLoading: usersLoading } = useQuery<User[]>({
    queryKey: ["/api/admin/users"],
    enabled: user?.role === "admin"
  });

  const { data: reports, isLoading: reportsLoading } = useQuery<(Report & { post: any; user: User })[]>({
    queryKey: ["/api/reports"],
    enabled: user?.role === "admin"
  });

  const { data: ads } = useQuery<Ad[]>({
    queryKey: ["/api/ads"],
    enabled: user?.role === "admin"
  });

  const { data: visitors } = useQuery<Visitor[]>({
    queryKey: ["/api/admin/unknown-visitors"],
    enabled: user?.role === "admin",
    refetchInterval: 30000
  });

  const { data: emergencyStatus } = useQuery<{ active: boolean; triggeredAt: string | null }>({
    queryKey: ["/api/admin/emergency-status"],
    enabled: user?.role === "admin"
  });

  const { data: collegeUsers } = useQuery<CollegeUser[]>({
    queryKey: ["/api/admin/college-users"],
    enabled: user?.role === "admin"
  });

  const { data: pendingUsers } = useQuery<PendingUser[]>({
    queryKey: ["/api/admin/pending-users"],
    enabled: user?.role === "admin",
    refetchInterval: 15000
  });

  const suspendUser = useMutation({
    mutationFn: async ({ id, reason }: { id: number; reason: string }) => {
      return apiRequest("POST", `/api/admin/users/${id}/suspend`, { reason });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/admin/users"] });
      toast({ title: "User suspended" });
    }
  });

  const unsuspendUser = useMutation({
    mutationFn: async (id: number) => {
      return apiRequest("POST", `/api/admin/users/${id}/unsuspend`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/admin/users"] });
      toast({ title: "User unsuspended" });
    }
  });

  const deleteUser = useMutation({
    mutationFn: async (id: number) => {
      return apiRequest("DELETE", `/api/admin/users/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/admin/users"] });
      toast({ title: "User deleted" });
    }
  });

  const warnUser = useMutation({
    mutationFn: async ({ id, message }: { id: number; message: string }) => {
      return apiRequest("POST", `/api/admin/users/${id}/warn`, { message });
    },
    onSuccess: () => {
      setWarningUserId(null);
      setWarningMessage("");
      toast({ title: "Warning sent to user" });
    }
  });

  const deletePost = useMutation({
    mutationFn: async (id: number) => {
      return apiRequest("DELETE", `/api/posts/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/reports"] });
      toast({ title: "Post deleted" });
    }
  });

  const deleteReport = useMutation({
    mutationFn: async (id: number) => {
      return apiRequest("DELETE", `/api/reports/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/reports"] });
      toast({ title: "Report dismissed" });
    }
  });

  const createAd = useMutation({
    mutationFn: async (data: typeof newAd) => {
      const formData = new FormData();
      formData.append('title', data.title);
      formData.append('linkUrl', data.linkUrl);
      if (adImage) {
        formData.append('image', adImage);
      }
      const res = await fetch('/api/ads', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });
      if (!res.ok) throw new Error('Failed');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/ads"] });
      setAdDialogOpen(false);
      setNewAd({ title: "", linkUrl: "" });
      setAdImage(null);
      toast({ title: "Ad created" });
    }
  });

  const deleteAd = useMutation({
    mutationFn: async (id: number) => {
      return apiRequest("DELETE", `/api/ads/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/ads"] });
      toast({ title: "Ad deleted" });
    }
  });

  const togglePremium = useMutation({
    mutationFn: async ({ id, isPremium }: { id: number; isPremium: boolean }) => {
      return apiRequest("POST", `/api/admin/users/${id}/premium`, { isPremium });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/admin/users"] });
      toast({ title: "Premium status updated" });
    }
  });

  const triggerEmergencyLogout = useMutation({
    mutationFn: async () => {
      return apiRequest("POST", "/api/admin/emergency-logout");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/admin/emergency-status"] });
      setEmergencyDialogOpen(false);
      toast({ title: "Emergency logout triggered - all users will be logged out", variant: "destructive" });
    }
  });

  const clearEmergencyLogout = useMutation({
    mutationFn: async () => {
      return apiRequest("DELETE", "/api/admin/emergency-logout");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/admin/emergency-status"] });
      toast({ title: "Emergency logout cleared - users can log in again" });
    }
  });

  const createCollegeUser = useMutation({
    mutationFn: async (data: typeof newCollegeUser) => {
      return apiRequest("POST", "/api/admin/college-users", data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/admin/college-users"] });
      setCollegeUserDialogOpen(false);
      setNewCollegeUser({ username: "", email: "", name: "", department: "" });
      toast({ title: "College user added to authorized list" });
    },
    onError: () => {
      toast({ title: "Failed to add user", variant: "destructive" });
    }
  });

  const deleteCollegeUser = useMutation({
    mutationFn: async (id: number) => {
      return apiRequest("DELETE", `/api/admin/college-users/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/admin/college-users"] });
      toast({ title: "College user removed from list" });
    }
  });

  const approvePendingUser = useMutation({
    mutationFn: async (id: number) => {
      return apiRequest("POST", `/api/admin/pending-users/${id}/approve`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/admin/pending-users"] });
      queryClient.invalidateQueries({ queryKey: ["/api/admin/users"] });
      toast({ title: "User approved - they can now log in!" });
    }
  });

  const rejectPendingUser = useMutation({
    mutationFn: async (id: number) => {
      return apiRequest("POST", `/api/admin/pending-users/${id}/reject`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/admin/pending-users"] });
      toast({ title: "User registration rejected" });
    }
  });

  if (user?.role !== "admin") {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="p-8 text-center">
          <AlertTriangle className="w-12 h-12 mx-auto mb-4 text-destructive" />
          <h1 className="text-xl font-bold mb-2">Access Denied</h1>
          <p className="text-muted-foreground">You need admin privileges to access this page.</p>
          <Link href="/">
            <Button className="mt-4">Go Home</Button>
          </Link>
        </Card>
      </div>
    );
  }

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
          <h1 className="text-3xl font-bold">Admin Dashboard</h1>
        </div>

        {/* Emergency Logout Banner */}
        {emergencyStatus?.active && (
          <Card className="mb-6 border-destructive bg-destructive/10">
            <CardContent className="flex items-center justify-between p-4">
              <div className="flex items-center gap-3">
                <AlertCircle className="w-6 h-6 text-destructive" />
                <div>
                  <p className="font-semibold text-destructive">Emergency Logout Active</p>
                  <p className="text-sm text-muted-foreground">All non-admin users are being logged out</p>
                </div>
              </div>
              <Button 
                variant="outline" 
                onClick={() => clearEmergencyLogout.mutate()}
                disabled={clearEmergencyLogout.isPending}
                data-testid="button-clear-emergency"
              >
                Clear Emergency
              </Button>
            </CardContent>
          </Card>
        )}

        <Tabs defaultValue="users" className="space-y-6">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="users" className="gap-2">
              <Users className="w-4 h-4" />
              <span className="hidden sm:inline">Users</span>
            </TabsTrigger>
            <TabsTrigger value="pending" className="gap-2 relative">
              <UserPlus className="w-4 h-4" />
              <span className="hidden sm:inline">Pending</span>
              {(pendingUsers?.length || 0) > 0 && (
                <Badge variant="destructive" className="absolute -top-1 -right-1 h-5 w-5 p-0 text-xs flex items-center justify-center">
                  {pendingUsers?.length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="college" className="gap-2">
              <GraduationCap className="w-4 h-4" />
              <span className="hidden sm:inline">College</span>
            </TabsTrigger>
            <TabsTrigger value="reports" className="gap-2">
              <Flag className="w-4 h-4" />
              <span className="hidden sm:inline">Reports</span> ({reports?.length || 0})
            </TabsTrigger>
            <TabsTrigger value="ads" className="gap-2">
              <Image className="w-4 h-4" />
              <span className="hidden sm:inline">Ads</span>
            </TabsTrigger>
            <TabsTrigger value="security" className="gap-2">
              <Shield className="w-4 h-4" />
              <span className="hidden sm:inline">Security</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="users">
            {usersLoading ? (
              <div className="flex justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
              </div>
            ) : (
              <div className="space-y-4">
                {users?.map((u) => (
                  <Card key={u.id} className={`p-4 ${u.isSuspended ? 'border-destructive/50 bg-destructive/5' : ''}`}>
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-xl">
                          {u.profileEmoji || "🎓"}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <p className="font-medium">{u.username}</p>
                            {(u as any).isPremium && (
                              <Badge variant="secondary" className="gap-1 bg-amber-500/20 text-amber-600">
                                <Crown className="w-3 h-3" />
                                Premium
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {u.role === "admin" ? "Admin" : "User"}
                            {u.isSuspended && " - Suspended"}
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        {/* Premium Toggle */}
                        <div className="flex items-center gap-2 px-2">
                          <Crown className={`w-4 h-4 ${(u as any).isPremium ? 'text-amber-500' : 'text-muted-foreground'}`} />
                          <Switch
                            checked={(u as any).isPremium || false}
                            onCheckedChange={(checked) => togglePremium.mutate({ id: u.id, isPremium: checked })}
                            data-testid={`switch-premium-${u.id}`}
                          />
                        </div>

                        <Dialog open={warningUserId === u.id} onOpenChange={(open) => !open && setWarningUserId(null)}>
                          <DialogTrigger asChild>
                            <Button variant="outline" size="sm" onClick={() => setWarningUserId(u.id)} data-testid={`button-warn-${u.id}`}>
                              <Send className="w-4 h-4 mr-1" />
                              Warn
                            </Button>
                          </DialogTrigger>
                          <DialogContent>
                            <DialogHeader>
                              <DialogTitle>Send Warning to {u.username}</DialogTitle>
                            </DialogHeader>
                            <Textarea 
                              placeholder="Warning message..."
                              value={warningMessage}
                              onChange={(e) => setWarningMessage(e.target.value)}
                            />
                            <Button onClick={() => warnUser.mutate({ id: u.id, message: warningMessage })}>
                              Send Warning
                            </Button>
                          </DialogContent>
                        </Dialog>

                        {u.isSuspended ? (
                          <Button variant="outline" size="sm" onClick={() => unsuspendUser.mutate(u.id)} data-testid={`button-unsuspend-${u.id}`}>
                            <CheckCircle className="w-4 h-4 mr-1" />
                            Unsuspend
                          </Button>
                        ) : (
                          <Button variant="outline" size="sm" onClick={() => suspendUser.mutate({ id: u.id, reason: "Violation of community guidelines" })} data-testid={`button-suspend-${u.id}`}>
                            <Ban className="w-4 h-4 mr-1" />
                            Suspend
                          </Button>
                        )}

                        <Button variant="destructive" size="sm" onClick={() => deleteUser.mutate(u.id)} data-testid={`button-delete-user-${u.id}`}>
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Pending Registrations Tab */}
          <TabsContent value="pending">
            <Card className="p-6">
              <div className="flex items-center gap-2 mb-4">
                <UserPlus className="w-5 h-5 text-primary" />
                <h3 className="text-lg font-semibold">Pending Registrations</h3>
                {(pendingUsers?.length || 0) > 0 && (
                  <Badge variant="destructive">{pendingUsers?.length} waiting</Badge>
                )}
              </div>
              
              {(pendingUsers?.length || 0) === 0 ? (
                <div className="text-center py-8">
                  <CheckCircle className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-muted-foreground">No pending registrations.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {pendingUsers?.map((pu) => (
                    <div key={pu.id} className="flex items-center justify-between p-4 border border-border rounded-lg bg-secondary/30">
                      <div>
                        <p className="font-medium">{pu.username}</p>
                        <p className="text-sm text-muted-foreground">{pu.email || "No email"}</p>
                        <p className="text-xs text-muted-foreground">
                          Registered: {pu.createdAt ? formatDistanceToNow(new Date(pu.createdAt), { addSuffix: true }) : "Unknown"}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          onClick={() => approvePendingUser.mutate(pu.id)}
                          disabled={approvePendingUser.isPending}
                          className="gap-1"
                          data-testid={`button-approve-${pu.id}`}
                        >
                          <Check className="w-4 h-4" />
                          Approve
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => rejectPendingUser.mutate(pu.id)}
                          disabled={rejectPendingUser.isPending}
                          className="gap-1"
                          data-testid={`button-reject-${pu.id}`}
                        >
                          <X className="w-4 h-4" />
                          Reject
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </TabsContent>

          {/* College Users Tab */}
          <TabsContent value="college">
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <GraduationCap className="w-5 h-5 text-primary" />
                  <h3 className="text-lg font-semibold">Authorized College Users</h3>
                </div>
                <Dialog open={collegeUserDialogOpen} onOpenChange={setCollegeUserDialogOpen}>
                  <DialogTrigger asChild>
                    <Button className="gap-2" data-testid="button-add-college-user">
                      <Plus className="w-4 h-4" />
                      Add User
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Add Authorized College User</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4 pt-4">
                      <Input
                        placeholder="Username (required)"
                        value={newCollegeUser.username}
                        onChange={(e) => setNewCollegeUser({ ...newCollegeUser, username: e.target.value })}
                        data-testid="input-college-username"
                      />
                      <Input
                        placeholder="Email"
                        value={newCollegeUser.email}
                        onChange={(e) => setNewCollegeUser({ ...newCollegeUser, email: e.target.value })}
                        data-testid="input-college-email"
                      />
                      <Input
                        placeholder="Full Name"
                        value={newCollegeUser.name}
                        onChange={(e) => setNewCollegeUser({ ...newCollegeUser, name: e.target.value })}
                        data-testid="input-college-name"
                      />
                      <Input
                        placeholder="Department"
                        value={newCollegeUser.department}
                        onChange={(e) => setNewCollegeUser({ ...newCollegeUser, department: e.target.value })}
                        data-testid="input-college-department"
                      />
                      <Button
                        onClick={() => createCollegeUser.mutate(newCollegeUser)}
                        disabled={!newCollegeUser.username || createCollegeUser.isPending}
                        className="w-full"
                        data-testid="button-save-college-user"
                      >
                        {createCollegeUser.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : "Add to Authorized List"}
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>

              <p className="text-sm text-muted-foreground mb-4">
                Only users in this list can register on the platform. Add students before they sign up.
              </p>

              {(collegeUsers?.length || 0) === 0 ? (
                <div className="text-center py-8">
                  <GraduationCap className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-muted-foreground">No authorized users yet. Add college students to allow them to register.</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {collegeUsers?.map((cu) => (
                    <div key={cu.id} className="flex items-center justify-between p-3 border border-border rounded-lg">
                      <div>
                        <p className="font-medium">{cu.username}</p>
                        <p className="text-sm text-muted-foreground">
                          {cu.name || "No name"} {cu.department && `• ${cu.department}`}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => deleteCollegeUser.mutate(cu.id)}
                        disabled={deleteCollegeUser.isPending}
                        data-testid={`button-delete-college-${cu.id}`}
                      >
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </TabsContent>

          <TabsContent value="reports">
            {reportsLoading ? (
              <div className="flex justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
              </div>
            ) : reports?.length === 0 ? (
              <div className="text-center py-12 glass-card rounded-2xl">
                <Flag className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">No reports to review.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {reports?.map((report) => (
                  <Card key={report.id} className="p-4">
                    <div className="flex justify-between items-start gap-4">
                      <div className="flex-1">
                        <p className="font-medium mb-1">Report #{report.id}</p>
                        <p className="text-sm text-muted-foreground mb-2">Reported by: {report.user?.username}</p>
                        <p className="text-sm mb-2"><strong>Reason:</strong> {report.reason}</p>
                        <p className="text-sm text-muted-foreground">Post: {report.post?.caption?.slice(0, 100) || report.post?.title}</p>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="destructive" size="sm" onClick={() => deletePost.mutate(report.postId)} data-testid={`button-delete-post-${report.id}`}>
                          Delete Post
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => deleteReport.mutate(report.id)} data-testid={`button-dismiss-${report.id}`}>
                          Dismiss
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="ads">
            <div className="flex justify-end mb-4">
              <Dialog open={adDialogOpen} onOpenChange={setAdDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="gap-2" data-testid="button-create-ad">
                    <Plus className="w-4 h-4" />
                    Create Ad
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Create New Ad</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4 pt-4">
                    <Input
                      placeholder="Ad title"
                      value={newAd.title}
                      onChange={(e) => setNewAd({ ...newAd, title: e.target.value })}
                    />
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-foreground">Ad Image (Required)</label>
                      <input
                        type="file"
                        ref={adFileInputRef}
                        accept="image/*,image/gif"
                        className="hidden"
                        onChange={(e) => setAdImage(e.target.files?.[0] || null)}
                      />
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => adFileInputRef.current?.click()}
                        className="w-full gap-2"
                      >
                        <ImageIcon className="w-4 h-4" />
                        {adImage ? adImage.name : "Choose Image/GIF"}
                      </Button>
                      {adImage && (
                        <img
                          src={URL.createObjectURL(adImage)}
                          alt="Preview"
                          className="w-full h-40 object-cover rounded-lg"
                        />
                      )}
                    </div>
                    
                    <Input
                      placeholder="Link URL (optional)"
                      value={newAd.linkUrl}
                      onChange={(e) => setNewAd({ ...newAd, linkUrl: e.target.value })}
                    />
                    <Button onClick={() => createAd.mutate(newAd)} disabled={!newAd.title || !adImage} className="w-full">
                      Create Ad
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              {ads?.map((ad) => (
                <Card key={ad.id} className="overflow-hidden">
                  <img src={ad.imageUrl} alt={ad.title} className="w-full max-w-[1080px] h-auto max-h-[400px] object-cover mx-auto" />
                  <CardContent className="p-4">
                    <div className="flex justify-between items-center">
                      <p className="font-medium">{ad.title}</p>
                      <Button variant="ghost" size="icon" onClick={() => deleteAd.mutate(ad.id)} className="text-destructive">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security">
            <div className="space-y-6">
              {/* Emergency Logout Section */}
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <AlertTriangle className="w-6 h-6 text-destructive" />
                    <div>
                      <h3 className="font-semibold text-lg">Emergency Logout</h3>
                      <p className="text-sm text-muted-foreground">Force logout all non-admin users immediately</p>
                    </div>
                  </div>
                  <Dialog open={emergencyDialogOpen} onOpenChange={setEmergencyDialogOpen}>
                    <DialogTrigger asChild>
                      <Button variant="destructive" className="gap-2" data-testid="button-emergency-logout">
                        <Shield className="w-4 h-4" />
                        Emergency Logout
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle className="text-destructive">Confirm Emergency Logout</DialogTitle>
                      </DialogHeader>
                      <div className="space-y-4 pt-4">
                        <p className="text-muted-foreground">
                          This will immediately log out ALL non-admin users and display a "Server Crashed" message.
                          Users will not be able to log back in until you clear this emergency state.
                        </p>
                        <div className="flex gap-2">
                          <Button variant="outline" onClick={() => setEmergencyDialogOpen(false)} className="flex-1">
                            Cancel
                          </Button>
                          <Button 
                            variant="destructive" 
                            onClick={() => triggerEmergencyLogout.mutate()}
                            disabled={triggerEmergencyLogout.isPending}
                            className="flex-1"
                            data-testid="button-confirm-emergency"
                          >
                            {triggerEmergencyLogout.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : "Trigger Logout"}
                          </Button>
                        </div>
                      </div>
                    </DialogContent>
                  </Dialog>
                </div>
              </Card>

              {/* Unknown Visitors Alert */}
              <Card className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Eye className="w-6 h-6 text-primary" />
                  <div>
                    <h3 className="font-semibold text-lg">Unknown Visitors Alert</h3>
                    <p className="text-sm text-muted-foreground">Recent unauthenticated visitors to the platform</p>
                  </div>
                </div>

                {visitors && visitors.length > 0 ? (
                  <div className="space-y-3 max-h-[400px] overflow-y-auto">
                    {visitors.map((visitor) => (
                      <div key={visitor.id} className="p-3 rounded-lg bg-secondary/50 border border-border">
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <Globe className="w-4 h-4 text-muted-foreground" />
                            <span className="font-mono text-sm">{visitor.ipAddress || 'Unknown IP'}</span>
                          </div>
                          <span className="text-xs text-muted-foreground">
                            {visitor.createdAt && formatDistanceToNow(new Date(visitor.createdAt), { addSuffix: true })}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1 truncate">
                          Path: {visitor.path}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1 truncate">
                          Browser: {visitor.userAgent?.slice(0, 80)}...
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <Eye className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p>No unknown visitors detected recently</p>
                  </div>
                )}
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
