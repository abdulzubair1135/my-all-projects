import { useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2, BookOpen, CheckCircle } from "lucide-react";

// Shared component for Login/Register to keep DRY
export default function AuthPage({ mode }: { mode: "login" | "register" }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [acceptedPolicy, setAcceptedPolicy] = useState(false);
  const [pendingApproval, setPendingApproval] = useState(false);
  const { login, register } = useAuth();
  const [, setLocation] = useLocation();

  const isLogin = mode === "login";
  const mutation = isLogin ? login : register;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isLogin && !acceptedPolicy) {
      alert("Please accept the Privacy Policy to register.");
      return;
    }
    const data = isLogin 
      ? { username, password } 
      : { username, password, email, phone, acceptedPrivacyPolicy: acceptedPolicy };
      
    mutation.mutate(
      data, 
      {
        onSuccess: (result: any) => {
          if (isLogin) {
            setLocation("/");
          } else if (result?.code === "PENDING_APPROVAL") {
            setPendingApproval(true);
          } else {
            setLocation("/login");
          }
        }
      }
    );
  };

  if (pendingApproval) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4 relative overflow-hidden">
        <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] rounded-full bg-primary/20 blur-[120px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] rounded-full bg-primary/10 blur-[120px]" />
        
        <div className="w-full max-w-md bg-card rounded-3xl p-8 relative z-10 border border-border shadow-2xl text-center">
          <CheckCircle className="w-16 h-16 mx-auto mb-6 text-green-500" />
          <h1 className="text-2xl font-bold mb-2 text-foreground">Registration Submitted!</h1>
          <p className="text-muted-foreground mb-6">
            Your account is pending admin approval. You'll be able to log in once an administrator approves your registration.
          </p>
          <Button onClick={() => setLocation("/login")} className="w-full" data-testid="button-back-to-login">
            Back to Login
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background Blobs */}
      <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] rounded-full bg-primary/20 blur-[120px]" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] rounded-full bg-primary/10 blur-[120px]" />

      <div className="w-full max-w-md bg-card rounded-3xl p-8 relative z-10 border border-border shadow-2xl">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-primary/70 mb-4 shadow-lg shadow-primary/30">
            <BookOpen className="w-6 h-6 text-primary-foreground" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight mb-2 text-foreground">
            {isLogin ? "Welcome Back" : "Join CampusHub"}
          </h1>
          <p className="text-muted-foreground">
            {isLogin ? "Enter your credentials to access your account" : "Connect with your campus community today"}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="username">Username</Label>
            <Input 
              id="username" 
              value={username} 
              onChange={(e) => setUsername(e.target.value)}
              className="bg-secondary border-border focus:ring-primary/50"
              placeholder="student_id"
              required 
              data-testid="input-username"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input 
              id="password" 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)}
              className="bg-secondary border-border focus:ring-primary/50"
              required 
              data-testid="input-password"
            />
          </div>

          {!isLogin && (
            <>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input 
                  id="email" 
                  type="email" 
                  value={email} 
                  onChange={(e) => setEmail(e.target.value)}
                  className="bg-secondary border-border focus:ring-primary/50"
                  placeholder="student@college.edu"
                  data-testid="input-email"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="phone">Phone Number</Label>
                <Input 
                  id="phone" 
                  value={phone} 
                  onChange={(e) => setPhone(e.target.value)}
                  className="bg-secondary border-border focus:ring-primary/50"
                  placeholder="+1 (555) 000-0000"
                  data-testid="input-phone"
                />
              </div>
              <div className="flex items-center gap-2 py-2">
                <input 
                  type="checkbox" 
                  id="policy" 
                  checked={acceptedPolicy}
                  onChange={(e) => setAcceptedPolicy(e.target.checked)}
                  className="rounded border-border bg-secondary text-primary focus:ring-primary/50"
                  data-testid="checkbox-policy"
                />
                <label htmlFor="policy" className="text-xs text-muted-foreground cursor-pointer hover:text-foreground transition-colors">
                  I agree to the <span className="text-primary">Privacy Policy</span>
                </label>
              </div>
            </>
          )}

          <Button 
            type="submit" 
            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold py-6 rounded-xl shadow-lg shadow-primary/20 transition-all hover:scale-[1.02]"
            disabled={mutation.isPending}
            data-testid="button-submit"
          >
            {mutation.isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : (isLogin ? "Sign In" : "Create Account")}
          </Button>
        </form>

        <div className="mt-6 text-center text-sm">
          <span className="text-muted-foreground">
            {isLogin ? "Don't have an account?" : "Already have an account?"}
          </span>
          <Button 
            variant="link" 
            className="text-primary hover:text-primary/80 pl-2"
            onClick={() => setLocation(isLogin ? "/register" : "/login")}
            data-testid="button-switch-auth"
          >
            {isLogin ? "Sign up" : "Log in"}
          </Button>
        </div>
      </div>
    </div>
  );
}
