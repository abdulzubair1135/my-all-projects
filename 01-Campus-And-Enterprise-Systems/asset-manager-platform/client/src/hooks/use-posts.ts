import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, buildUrl, type InsertPost, type InsertComment } from "@shared/routes";
import { useToast } from "@/hooks/use-toast";
import type { UpdatePost } from "@shared/schema";

type PostFilters = {
  category?: string;
  sort?: 'latest' | 'top';
  search?: string;
  trending?: boolean;
};

export function usePosts(filters?: PostFilters) {
  const queryString = new URLSearchParams(
    Object.entries(filters || {}).reduce((acc, [key, val]) => {
      if (val !== undefined) acc[key] = String(val);
      return acc;
    }, {} as Record<string, string>)
  ).toString();

  const queryKey = [api.posts.list.path, queryString];

  return useQuery({
    queryKey,
    queryFn: async () => {
      const url = `${api.posts.list.path}?${queryString}`;
      const res = await fetch(url, { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch posts");
      return api.posts.list.responses[200].parse(await res.json());
    },
  });
}

export function useCreatePost() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: async (data: FormData | InsertPost) => {
      let res: Response;
      
      if (data instanceof FormData) {
        res = await fetch(api.posts.create.path, {
          method: api.posts.create.method,
          body: data,
          credentials: "include",
        });
      } else {
        res = await fetch(api.posts.create.path, {
          method: api.posts.create.method,
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
          credentials: "include",
        });
      }

      if (!res.ok) {
        const error = await res.json().catch(() => ({ message: "Failed to create post" }));
        throw new Error(error.message || "Failed to create post");
      }
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [api.posts.list.path] });
      toast({ title: "Posted!", description: "Your post is now live." });
    },
    onError: (error: Error) => {
      toast({ title: "Error", description: error.message || "Could not create post.", variant: "destructive" });
    },
  });
}

export function useLikePost() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (postId: number) => {
      const url = buildUrl(api.posts.like.path, { id: postId });
      const res = await fetch(url, { 
        method: api.posts.like.method, 
        credentials: "include" 
      });
      if (!res.ok) throw new Error("Failed to like post");
      return api.posts.like.responses[200].parse(await res.json());
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [api.posts.list.path] });
    },
  });
}

export function useDeletePost() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: async (postId: number) => {
      const url = buildUrl(api.posts.delete.path, { id: postId });
      const res = await fetch(url, { 
        method: api.posts.delete.method, 
        credentials: "include" 
      });
      if (!res.ok) throw new Error("Failed to delete post");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [api.posts.list.path] });
      toast({ title: "Deleted", description: "Post has been removed." });
    },
  });
}

export function useCreateComment() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: async ({ postId, text }: { postId: number; text: string }) => {
      const url = buildUrl(api.comments.create.path, { postId });
      const res = await fetch(url, {
        method: api.comments.create.method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to comment");
      return api.comments.create.responses[201].parse(await res.json());
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [api.posts.list.path] });
      toast({ title: "Commented", description: "Your comment was added." });
    },
  });
}

export function useReportPost() {
  const { toast } = useToast();

  return useMutation({
    mutationFn: async ({ postId, reason }: { postId: number; reason: string }) => {
      const url = buildUrl(api.reports.create.path, { postId });
      const res = await fetch(url, {
        method: api.reports.create.method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason }),
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to report");
      return api.reports.create.responses[201].parse(await res.json());
    },
    onSuccess: () => {
      toast({ title: "Report Submitted", description: "Thank you for keeping the community safe." });
    },
  });
}

export function useUpdatePost() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: UpdatePost }) => {
      const res = await fetch(`/api/posts/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to update post");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [api.posts.list.path] });
      toast({ title: "Post updated", description: "Your changes have been saved." });
    },
    onError: () => {
      toast({ title: "Error", description: "Could not update post.", variant: "destructive" });
    },
  });
}
