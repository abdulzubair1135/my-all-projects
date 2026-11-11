import { useState } from "react";
import { formatDistanceToNow } from "date-fns";
import { 
  Heart, 
  MessageSquare, 
  Share2, 
  MoreHorizontal, 
  Download,
  Flag,
  User as UserIcon,
  Edit2
} from "lucide-react";
import { type PostWithDetails, type UpdatePost } from "@shared/schema";
import { useAuth } from "@/hooks/use-auth";
import { useLikePost, useDeletePost, useCreateComment, useReportPost, useUpdatePost } from "@/hooks/use-posts";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

export function PostCard({ post }: { post: PostWithDetails }) {
  const { user } = useAuth();
  const { mutate: likePost } = useLikePost();
  const { mutate: deletePost } = useDeletePost();
  const { mutate: addComment } = useCreateComment();
  const { mutate: reportPost } = useReportPost();
  const { mutate: updatePost } = useUpdatePost();

  const [commentText, setCommentText] = useState("");
  const [showComments, setShowComments] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editCaption, setEditCaption] = useState(post.caption || "");
  const [editTitle, setEditTitle] = useState(post.title || "");

  const isAuthor = user?.id === post.userId;

  const handleUpdate = (e: React.FormEvent) => {
    e.preventDefault();
    updatePost({ 
      id: post.id, 
      data: { caption: editCaption, title: editTitle } 
    });
    setIsEditing(false);
  };
  const isConfession = post.type === "confession";
  const isNote = post.type === "notes";

  const handleComment = (e: React.FormEvent) => {
    e.preventDefault();
    if (!commentText.trim()) return;
    addComment({ postId: post.id, text: commentText });
    setCommentText("");
  };

  return (
    <div className={`
      glass-card rounded-2xl p-6 mb-6 transition-all duration-300 hover:border-border
      ${isConfession ? "border-l-4 border-l-rose-500" : ""}
      ${isNote ? "border-l-4 border-l-emerald-500" : ""}
    `} data-testid={`post-card-${post.id}`}>
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-3">
          <div className={`
            w-10 h-10 rounded-full flex items-center justify-center
            ${isConfession ? "bg-rose-500/10 text-rose-500" : "bg-primary/10 text-primary"}
          `}>
            {isConfession ? <UserIcon className="w-5 h-5" /> : post.user?.username.charAt(0).toUpperCase()}
          </div>
          <div>
            <h4 className="font-semibold text-sm text-foreground">
              {isConfession ? "Anonymous Student" : post.user?.username}
            </h4>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span>{formatDistanceToNow(new Date(post.createdAt!), { addSuffix: true })}</span>
              {isNote && (
                <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                  {post.subject}
                </span>
              )}
            </div>
          </div>
        </div>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground" data-testid={`button-post-menu-${post.id}`}>
              <MoreHorizontal className="w-4 h-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {isAuthor && (
              <>
                <Dialog open={isEditing} onOpenChange={setIsEditing}>
                  <DialogTrigger asChild>
                    <DropdownMenuItem onSelect={(e) => e.preventDefault()}>
                      <Edit2 className="w-4 h-4 mr-2" /> Edit
                    </DropdownMenuItem>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Edit Post</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={handleUpdate} className="space-y-4">
                      {isNote && (
                        <div className="space-y-2">
                          <Label>Title</Label>
                          <Input 
                            value={editTitle} 
                            onChange={e => setEditTitle(e.target.value)}
                            className="bg-secondary/50 border-border"
                          />
                        </div>
                      )}
                      <div className="space-y-2">
                        <Label>Caption</Label>
                        <Textarea 
                          value={editCaption} 
                          onChange={e => setEditCaption(e.target.value)}
                          className="bg-secondary/50 border-border min-h-[100px]"
                        />
                      </div>
                      <Button type="submit" className="w-full">
                        Save Changes
                      </Button>
                    </form>
                  </DialogContent>
                </Dialog>
                <DropdownMenuItem 
                  onClick={() => deletePost(post.id)}
                  className="text-destructive focus:text-destructive"
                  data-testid={`button-delete-post-${post.id}`}
                >
                  Delete
                </DropdownMenuItem>
              </>
            )}
            {!isAuthor && (
              <DropdownMenuItem onClick={() => reportPost({ postId: post.id, reason: "Inappropriate" })}>
                <Flag className="w-4 h-4 mr-2" /> Report
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <div className="mb-4 space-y-3">
        {isNote && (
          <h3 className="text-lg font-bold text-emerald-600 dark:text-emerald-400">{post.title}</h3>
        )}
        <p className="text-foreground/80 whitespace-pre-wrap leading-relaxed">{post.caption}</p>
        
        {post.fileUrl && post.fileType?.startsWith('image/') && (
          <div className="rounded-xl overflow-hidden border border-border">
            <img 
              src={post.fileUrl} 
              alt="Post image" 
              className="w-full max-w-[1080px] h-auto object-contain mx-auto"
              loading="lazy"
            />
          </div>
        )}
        
        {post.fileUrl && !post.fileType?.startsWith('image/') && (
          <div className="flex items-center gap-4 p-4 rounded-xl bg-secondary/50 border border-border hover:bg-secondary transition-colors cursor-pointer group">
            <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center text-primary">
              <Download className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-foreground">{post.fileUrl.split('/').pop()}</p>
              <p className="text-xs text-muted-foreground">{post.fileType}</p>
            </div>
            <a href={post.fileUrl} target="_blank" rel="noopener noreferrer">
              <Button size="sm" variant="ghost" className="opacity-0 group-hover:opacity-100 transition-opacity">
                Download
              </Button>
            </a>
          </div>
        )}

        {isNote && !post.fileUrl && (
          <div className="flex items-center gap-4 p-4 rounded-xl bg-secondary/50 border border-border hover:bg-secondary transition-colors cursor-pointer group">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
              <Download className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-foreground">Lecture_Notes.pdf</p>
              <p className="text-xs text-muted-foreground">2.4 MB</p>
            </div>
            <Button size="sm" variant="ghost" className="opacity-0 group-hover:opacity-100 transition-opacity">
              Download
            </Button>
          </div>
        )}
      </div>

      <div className="flex items-center gap-4 pt-4 border-t border-border">
        <Button 
          variant="ghost" 
          size="sm"
          onClick={() => likePost(post.id)}
          className={`gap-2 ${post.hasLiked ? "text-rose-500" : "text-muted-foreground hover:text-rose-500"}`}
          data-testid={`button-like-${post.id}`}
        >
          <Heart className={`w-4 h-4 ${post.hasLiked ? "fill-current" : ""}`} />
          {post.likeCount}
        </Button>

        <Button 
          variant="ghost" 
          size="sm" 
          className="gap-2 text-muted-foreground hover:text-primary"
          onClick={() => setShowComments(!showComments)}
          data-testid={`button-comments-${post.id}`}
        >
          <MessageSquare className="w-4 h-4" />
          {post.comments.length}
        </Button>

        <Button variant="ghost" size="sm" className="gap-2 text-muted-foreground hover:text-primary ml-auto" data-testid={`button-share-${post.id}`}>
          <Share2 className="w-4 h-4" />
        </Button>
      </div>

      {showComments && (
        <div className="mt-4 pt-4 space-y-4 border-t border-border animate-in slide-in-from-top-2">
          {post.comments.map((comment) => (
            <div key={comment.id} className="flex gap-3 text-sm">
              <div className="font-bold text-primary shrink-0">
                {comment.user.username}
              </div>
              <div className="text-muted-foreground">{comment.text}</div>
            </div>
          ))}
          
          {user && (
            <form onSubmit={handleComment} className="flex gap-2 mt-4">
              <Input 
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                placeholder="Write a comment..."
                className="bg-secondary/50 border-border h-9 text-sm"
                data-testid={`input-comment-${post.id}`}
              />
              <Button type="submit" size="sm" variant="secondary" disabled={!commentText.trim()} data-testid={`button-submit-comment-${post.id}`}>
                Post
              </Button>
            </form>
          )}
        </div>
      )}
    </div>
  );
}
