import { useState, useRef } from "react";
import { useAuth } from "@/hooks/use-auth";
import { useCreatePost } from "@/hooks/use-posts";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { 
  Image as ImageIcon, 
  FileText, 
  MessageCircle, 
  Send,
  Lock,
  X
} from "lucide-react";

export function PostComposer() {
  const { user } = useAuth();
  const { mutate: createPost, isPending } = useCreatePost();
  
  const [postType, setPostType] = useState<"normal" | "notes" | "confession">("normal");
  const [category, setCategory] = useState("general");
  const [caption, setCaption] = useState("");
  const [title, setTitle] = useState("");
  const [subject, setSubject] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      if (file.type.startsWith("image/")) {
        const url = URL.createObjectURL(file);
        setPreviewUrl(url);
      } else {
        setPreviewUrl(null);
      }
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleSubmit = () => {
    if (!caption && postType !== "notes") return;
    if (postType === "notes" && (!title || !subject)) return;

    const formData = new FormData();
    formData.append("type", postType);
    formData.append("category", postType === "confession" ? "confession" : (postType === "notes" ? "notes" : category));
    formData.append("caption", caption);
    formData.append("isAnonymous", String(postType === "confession"));
    
    if (postType === "notes") {
      formData.append("title", title);
      formData.append("subject", subject);
    }
    
    if (selectedFile) {
      formData.append("file", selectedFile);
    }

    createPost(formData as any, {
      onSuccess: () => {
        setCaption("");
        setTitle("");
        setSubject("");
        clearFile();
        setPostType("normal");
        setCategory("general");
      }
    });
  };

  if (!user) {
    return (
      <div className="glass-card rounded-2xl p-6 mb-6 text-center">
        <h3 className="text-lg font-semibold mb-2">Join the conversation</h3>
        <p className="text-muted-foreground mb-4">Log in to share your thoughts, notes, and confessions.</p>
        <Button className="bg-primary hover:bg-primary/90">Log in to Post</Button>
      </div>
    );
  }

  return (
    <div className="glass-card rounded-2xl p-6 mb-6 animate-in fade-in slide-in-from-top-4 duration-500">
      <div className="space-y-4">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[140px]">
            <Label className="text-sm mb-2 block text-muted-foreground">Post Type</Label>
            <Select value={postType} onValueChange={(v: any) => setPostType(v)}>
              <SelectTrigger className="bg-secondary/50 border-border" data-testid="select-post-type">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="normal">
                  <div className="flex items-center gap-2">
                    <MessageCircle className="w-4 h-4" />
                    Regular Post
                  </div>
                </SelectItem>
                <SelectItem value="notes">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    Academic Notes
                  </div>
                </SelectItem>
                <SelectItem value="confession">
                  <div className="flex items-center gap-2">
                    <Lock className="w-4 h-4" />
                    Anonymous Confession
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          {postType === "normal" && (
            <div className="flex-1 min-w-[140px]">
              <Label className="text-sm mb-2 block text-muted-foreground">Category</Label>
              <Select value={category} onValueChange={setCategory}>
                <SelectTrigger className="bg-secondary/50 border-border" data-testid="select-category">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="general">General</SelectItem>
                  <SelectItem value="memes">Memes</SelectItem>
                  <SelectItem value="questions">Questions</SelectItem>
                  <SelectItem value="events">Events</SelectItem>
                  <SelectItem value="clubs">Clubs</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}
        </div>

        {postType === "notes" && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-sm mb-2 block text-muted-foreground">Subject/Course</Label>
              <Input 
                placeholder="e.g. CS101" 
                className="bg-secondary/50 border-border"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                data-testid="input-subject"
              />
            </div>
            <div>
              <Label className="text-sm mb-2 block text-muted-foreground">Title</Label>
              <Input 
                placeholder="Note Title" 
                className="bg-secondary/50 border-border"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                data-testid="input-title"
              />
            </div>
          </div>
        )}

        <Textarea 
          placeholder={
            postType === "confession" 
              ? "Speak your mind anonymously..." 
              : postType === "notes" 
                ? "Describe these notes..." 
                : "What's happening on campus?"
          }
          className="min-h-[100px] bg-secondary/50 border-border resize-none focus:ring-1 focus:ring-primary/50"
          value={caption}
          onChange={(e) => setCaption(e.target.value)}
          data-testid="input-caption"
        />

        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          accept="image/*,.pdf"
          className="hidden"
        />

        {selectedFile && (
          <div className="flex items-center gap-3 p-3 rounded-lg bg-secondary/50 border border-border">
            {previewUrl ? (
              <img src={previewUrl} alt="Preview" className="w-16 h-16 object-cover rounded-md" />
            ) : (
              <div className="w-16 h-16 rounded-md bg-primary/10 flex items-center justify-center">
                <FileText className="w-8 h-8 text-primary" />
              </div>
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{selectedFile.name}</p>
              <p className="text-xs text-muted-foreground">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            <Button variant="ghost" size="icon" onClick={clearFile} data-testid="button-clear-file">
              <X className="w-4 h-4" />
            </Button>
          </div>
        )}

        <div className="flex justify-between items-center pt-2">
          <div className="flex gap-2">
            <Button 
              variant="ghost" 
              size="icon" 
              className="text-muted-foreground hover:text-primary"
              onClick={() => fileInputRef.current?.click()}
              data-testid="button-add-image"
            >
              <ImageIcon className="w-5 h-5" />
            </Button>
            {postType === "notes" && (
              <Button 
                variant="ghost" 
                size="icon" 
                className="text-muted-foreground hover:text-primary"
                onClick={() => fileInputRef.current?.click()}
                data-testid="button-add-pdf"
              >
                <FileText className="w-5 h-5" />
              </Button>
            )}
          </div>
          
          <Button 
            onClick={handleSubmit} 
            disabled={isPending}
            className={`
              px-6 rounded-xl font-semibold shadow-lg transition-all
              ${postType === "confession" 
                ? "bg-rose-600 hover:bg-rose-700 shadow-rose-600/20" 
                : "bg-primary hover:bg-primary/90 shadow-primary/20"
              }
            `}
            data-testid="button-post-submit"
          >
            {isPending ? "Posting..." : "Post"} 
            <Send className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </div>
    </div>
  );
}
