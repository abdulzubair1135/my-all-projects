import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ThemeProvider } from "@/components/ThemeProvider";
import NotFound from "@/pages/not-found";
import Home from "@/pages/Home";
import AuthPage from "@/pages/Auth";
import Profile from "@/pages/Profile";
import Events from "@/pages/Events";
import Settings from "@/pages/Settings";
import Admin from "@/pages/Admin";
import Messages from "@/pages/Messages";
import Community from "@/pages/Community";
import Help from "@/pages/Help";
import { Topbar } from "@/components/Navigation";

function Router() {
  return (
    <div className="min-h-screen bg-background">
      <main>
        <Switch>
          <Route path="/" component={Home} />
          <Route path="/login">
            <AuthPage mode="login" />
          </Route>
          <Route path="/register">
            <AuthPage mode="register" />
          </Route>
          <Route path="/profile/:username" component={Profile} />
          <Route path="/events" component={Events} />
          <Route path="/settings" component={Settings} />
          <Route path="/admin" component={Admin} />
          <Route path="/messages" component={Messages} />
          <Route path="/community" component={Community} />
          <Route path="/help" component={Help} />
          <Route component={NotFound} />
        </Switch>
      </main>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
