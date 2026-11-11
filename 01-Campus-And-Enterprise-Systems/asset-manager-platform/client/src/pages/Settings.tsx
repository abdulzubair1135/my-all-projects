import { useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useToast } from "@/hooks/use-toast";
import { User, Shield, Lock, Bell, UserCircle, Key } from "lucide-react";
import { apiRequest } from "@/lib/queryClient";

const EMOJIS = ["🎓", "👨‍🎓", "👩‍🎓", "🏫", "📚", "🖊️", "🔬", "🎨", "🎭", "🏃", "⚽", "🍕", "☕", "🎸", "💻", "🧠"];

export default function Settings() {
  const { user } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  const [name, setName] = useState(user?.name || "");
  const [bio, setBio] = useState(user?.bio || "");
  const [profileEmoji, setProfileEmoji] = useState(user?.profileEmoji || "🎓");
  const [isPrivate, setIsPrivate] = useState(user?.isPrivate || false);
  
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const updateMutation = useMutation({
    mutationFn: async (data: any) => {
      const res = await apiRequest("PATCH", "/api/user", data);
      return res.json();
    },
    onSuccess: (updatedUser) => {
      queryClient.setQueryData(["/api/user"], updatedUser);
      toast({ title: "Settings updated", description: "Your changes have been saved." });
    }
  });

  const passwordMutation = useMutation({
    mutationFn: async (data: { currentPassword: string; newPassword: string }) => {
      const res = await apiRequest("POST", "/api/user/change-password", data);
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.message || "Failed to change password");
      }
      return res.json();
    },
    onSuccess: () => {
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      toast({ title: "Password changed", description: "Your password has been updated." });
    },
    onError: (error: Error) => {
      toast({ title: "Error", description: error.message, variant: "destructive" });
    }
  });

  const handleSave = () => {
    updateMutation.mutate({ name, bio, profileEmoji, isPrivate });
  };

  const handlePasswordChange = () => {
    if (newPassword !== confirmPassword) {
      toast({ title: "Error", description: "New passwords do not match.", variant: "destructive" });
      return;
    }
    if (newPassword.length < 6) {
      toast({ title: "Error", description: "Password must be at least 6 characters.", variant: "destructive" });
      return;
    }
    passwordMutation.mutate({ currentPassword, newPassword });
  };

  return (
    <div className="p-8 max-w-2xl mx-auto space-y-8 pb-20">
      <h1 className="text-4xl font-bold tracking-tight text-white mb-8">Settings</h1>

      {/* Profile Section */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <UserCircle className="w-5 h-5" />
            Profile Settings
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label className="text-white">Profile Emoji</Label>
            <div className="grid grid-cols-8 gap-2">
              {EMOJIS.map(emoji => (
                <button
                  key={emoji}
                  onClick={() => setProfileEmoji(emoji)}
                  className={`text-2xl p-2 rounded-lg transition-all ${profileEmoji === emoji ? 'bg-indigo-600/40 ring-2 ring-indigo-500' : 'hover:bg-white/5'}`}
                >
                  {emoji}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="name" className="text-white">Display Name</Label>
            <Input 
              id="name" 
              value={name} 
              onChange={e => setName(e.target.value)}
              className="bg-black/40 border-white/10"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="bio" className="text-white">Bio</Label>
            <Input 
              id="bio" 
              value={bio} 
              onChange={e => setBio(e.target.value)}
              className="bg-black/40 border-white/10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Privacy Section */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Lock className="w-5 h-5" />
            Privacy & Security
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-white">Private Profile</Label>
              <p className="text-sm text-muted-foreground">Only students you approve can see your posts.</p>
            </div>
            <Switch checked={isPrivate} onCheckedChange={setIsPrivate} />
          </div>

          <div className="pt-4 border-t border-white/5">
            <h4 className="text-sm font-medium text-white mb-2 flex items-center gap-2">
              <Shield className="w-4 h-4 text-indigo-400" />
              Privacy Policy
            </h4>
            <p className="text-xs text-muted-foreground">
              CampusHub is committed to protecting your privacy. We never share your academic data with third parties.
              Anonymous confessions are truly anonymous - we do not store metadata that links them to your identity.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Password Change Section */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Key className="w-5 h-5" />
            Change Password
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="currentPassword" className="text-white">Current Password</Label>
            <Input 
              id="currentPassword" 
              type="password"
              value={currentPassword} 
              onChange={e => setCurrentPassword(e.target.value)}
              className="bg-black/40 border-white/10"
              data-testid="input-current-password"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="newPassword" className="text-white">New Password</Label>
            <Input 
              id="newPassword" 
              type="password"
              value={newPassword} 
              onChange={e => setNewPassword(e.target.value)}
              className="bg-black/40 border-white/10"
              data-testid="input-new-password"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="confirmPassword" className="text-white">Confirm New Password</Label>
            <Input 
              id="confirmPassword" 
              type="password"
              value={confirmPassword} 
              onChange={e => setConfirmPassword(e.target.value)}
              className="bg-black/40 border-white/10"
              data-testid="input-confirm-password"
            />
          </div>
          <Button 
            onClick={handlePasswordChange} 
            disabled={passwordMutation.isPending || !currentPassword || !newPassword || !confirmPassword}
            className="w-full bg-amber-600 hover:bg-amber-700"
            data-testid="button-change-password"
          >
            {passwordMutation.isPending ? "Changing..." : "Change Password"}
          </Button>
        </CardContent>
      </Card>

      <Button 
        onClick={handleSave} 
        disabled={updateMutation.isPending}
        className="w-full bg-indigo-600 hover:bg-indigo-700 py-6 rounded-xl text-lg font-semibold"
        data-testid="button-save-settings"
      >
        {updateMutation.isPending ? "Saving..." : "Save Changes"}
      </Button>
    </div>
  );
}
