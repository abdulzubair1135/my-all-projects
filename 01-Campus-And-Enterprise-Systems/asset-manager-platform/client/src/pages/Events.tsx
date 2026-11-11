import { useState, useRef } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Event } from "@shared/schema";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Calendar, MapPin, Clock, ArrowLeft, Plus, Trash2, Loader2, ImageIcon } from "lucide-react";
import { format } from "date-fns";
import { Link } from "wouter";
import { useAuth } from "@/hooks/use-auth";
import { queryClient } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Sidebar, Topbar } from "@/components/Navigation";

export default function EventsPage() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [open, setOpen] = useState(false);
  const [newEvent, setNewEvent] = useState({ title: "", description: "", date: "", location: "" });
  const [eventImage, setEventImage] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { data: events, isLoading } = useQuery<Event[]>({
    queryKey: ["/api/events"],
  });

  const createEvent = useMutation({
    mutationFn: async (data: typeof newEvent) => {
      const formData = new FormData();
      formData.append('title', data.title);
      formData.append('description', data.description);
      formData.append('date', new Date(data.date).toISOString());
      formData.append('location', data.location);
      if (eventImage) {
        formData.append('image', eventImage);
      }
      
      const res = await fetch('/api/events', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });
      if (!res.ok) throw new Error('Failed to create event');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/events"] });
      setOpen(false);
      setNewEvent({ title: "", description: "", date: "", location: "" });
      setEventImage(null);
      toast({ title: "Event created successfully" });
    },
    onError: () => {
      toast({ title: "Failed to create event", variant: "destructive" });
    }
  });

  const deleteEvent = useMutation({
    mutationFn: async (id: number) => {
      const res = await fetch(`/api/events/${id}`, { method: 'DELETE', credentials: 'include' });
      if (!res.ok) throw new Error('Failed');
      return res;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/events"] });
      toast({ title: "Event deleted" });
    }
  });

  const isAdmin = user?.role === "admin";

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Topbar />
      <Sidebar />

      <main className="pt-24 lg:pl-72 pb-12 px-4 max-w-5xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="ghost" size="icon" data-testid="button-back">
                <ArrowLeft className="w-5 h-5" />
              </Button>
            </Link>
            <h1 className="text-3xl font-bold tracking-tight">Campus Events</h1>
          </div>
          
          {isAdmin && (
            <Dialog open={open} onOpenChange={setOpen}>
              <DialogTrigger asChild>
                <Button className="gap-2" data-testid="button-create-event">
                  <Plus className="w-4 h-4" />
                  Create Event
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create New Event</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 pt-4">
                  <Input
                    placeholder="Event title"
                    value={newEvent.title}
                    onChange={(e) => setNewEvent({ ...newEvent, title: e.target.value })}
                    data-testid="input-event-title"
                  />
                  <Textarea
                    placeholder="Description"
                    value={newEvent.description}
                    onChange={(e) => setNewEvent({ ...newEvent, description: e.target.value })}
                    data-testid="input-event-description"
                  />
                  <Input
                    type="datetime-local"
                    value={newEvent.date}
                    onChange={(e) => setNewEvent({ ...newEvent, date: e.target.value })}
                    data-testid="input-event-date"
                  />
                  <Input
                    placeholder="Location"
                    value={newEvent.location}
                    onChange={(e) => setNewEvent({ ...newEvent, location: e.target.value })}
                    data-testid="input-event-location"
                  />
                  
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-foreground">Event Image (Required)</label>
                    <input
                      type="file"
                      ref={fileInputRef}
                      accept="image/*"
                      className="hidden"
                      onChange={(e) => setEventImage(e.target.files?.[0] || null)}
                    />
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => fileInputRef.current?.click()}
                      className="w-full gap-2"
                      data-testid="button-upload-event-image"
                    >
                      <ImageIcon className="w-4 h-4" />
                      {eventImage ? eventImage.name : "Choose Image"}
                    </Button>
                    {eventImage && (
                      <img
                        src={URL.createObjectURL(eventImage)}
                        alt="Preview"
                        className="w-full h-40 object-cover rounded-lg"
                      />
                    )}
                  </div>
                  
                  <Button 
                    onClick={() => createEvent.mutate(newEvent)} 
                    disabled={createEvent.isPending || !newEvent.title || !newEvent.date || !eventImage}
                    className="w-full"
                    data-testid="button-submit-event"
                  >
                    {createEvent.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : "Create Event"}
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          )}
        </div>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : events?.length === 0 ? (
          <div className="text-center py-12 glass-card rounded-2xl">
            <Calendar className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-muted-foreground">No upcoming events.</p>
          </div>
        ) : (
          <div className="grid gap-6">
            {events?.map((event) => (
              <Card key={event.id} className="glass-card border-border overflow-hidden hover-elevate transition-all">
                {(event as any).imageUrl && (
                  <div className="w-full">
                    <img 
                      src={(event as any).imageUrl} 
                      alt={event.title} 
                      className="w-full max-w-[1080px] h-auto max-h-[400px] object-cover mx-auto"
                    />
                  </div>
                )}
                <CardHeader className="flex flex-row items-start justify-between space-y-0 gap-4 pb-2">
                  <div className="space-y-1 flex-1">
                    <CardTitle className="text-2xl font-bold">{event.title}</CardTitle>
                    <div className="flex flex-wrap items-center text-sm text-muted-foreground gap-4">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {format(new Date(event.date), "PPP")}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {format(new Date(event.date), "p")}
                      </span>
                      {event.location && (
                        <span className="flex items-center gap-1">
                          <MapPin className="w-4 h-4" />
                          {event.location}
                        </span>
                      )}
                    </div>
                  </div>
                  {isAdmin && (
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      onClick={() => deleteEvent.mutate(event.id)}
                      className="text-destructive hover:text-destructive"
                      data-testid={`button-delete-event-${event.id}`}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  )}
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground whitespace-pre-wrap">{event.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
