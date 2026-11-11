import { z } from 'zod';
import { insertPostSchema, insertCommentSchema, insertReportSchema, insertUserSchema } from './schema';

export const errorSchemas = {
  validation: z.object({
    message: z.string(),
    field: z.string().optional(),
  }),
  notFound: z.object({
    message: z.string(),
  }),
  unauthorized: z.object({
    message: z.string(),
  }),
  internal: z.object({
    message: z.string(),
  }),
};

export const api = {
  auth: {
    register: {
      method: 'POST' as const,
      path: '/api/auth/register',
      input: insertUserSchema,
      responses: {
        201: z.object({ id: z.number(), username: z.string() }), // Return minimal user info
        400: errorSchemas.validation,
      },
    },
    login: {
      method: 'POST' as const,
      path: '/api/auth/login',
      input: z.object({ username: z.string(), password: z.string() }),
      responses: {
        200: z.object({ id: z.number(), username: z.string() }),
        401: errorSchemas.unauthorized,
      },
    },
    logout: {
      method: 'POST' as const,
      path: '/api/auth/logout',
      responses: {
        200: z.object({ message: z.string() }),
      },
    },
    me: {
      method: 'GET' as const,
      path: '/api/user',
      responses: {
        200: z.custom<any>(), // Returns User object
        401: errorSchemas.unauthorized,
      },
    },
  },
  posts: {
    list: {
      method: 'GET' as const,
      path: '/api/posts',
      input: z.object({
        category: z.string().optional(),
        sort: z.enum(['latest', 'top']).optional(),
        search: z.string().optional(),
        trending: z.boolean().optional(),
      }).optional(),
      responses: {
        200: z.array(z.custom<any>()), // Returns PostWithDetails[]
      },
    },
    create: {
      method: 'POST' as const,
      path: '/api/posts',
      // Note: Actual request is multipart/form-data. This schema validates the JSON fields.
      input: insertPostSchema.omit({ userId: true, fileUrl: true, fileType: true }),
      responses: {
        201: z.custom<any>(),
        401: errorSchemas.unauthorized,
      },
    },
    get: {
      method: 'GET' as const,
      path: '/api/posts/:id',
      responses: {
        200: z.custom<any>(),
        404: errorSchemas.notFound,
      },
    },
    delete: {
      method: 'DELETE' as const,
      path: '/api/posts/:id',
      responses: {
        200: z.void(),
        401: errorSchemas.unauthorized,
        403: errorSchemas.unauthorized, // Forbidden (not owner)
      },
    },
    like: {
      method: 'POST' as const,
      path: '/api/posts/:id/like',
      responses: {
        200: z.object({ likes: z.number(), hasLiked: z.boolean() }),
        401: errorSchemas.unauthorized,
      },
    },
  },
  comments: {
    create: {
      method: 'POST' as const,
      path: '/api/posts/:postId/comments',
      input: z.object({ text: z.string() }),
      responses: {
        201: z.custom<any>(),
        401: errorSchemas.unauthorized,
      },
    },
  },
  reports: {
    create: {
      method: 'POST' as const,
      path: '/api/posts/:postId/report',
      input: z.object({ reason: z.string() }),
      responses: {
        201: z.custom<any>(),
        401: errorSchemas.unauthorized,
      },
    },
    list: {
      method: 'GET' as const,
      path: '/api/admin/reports',
      responses: {
        200: z.array(z.custom<any>()),
        403: errorSchemas.unauthorized,
      },
    },
  }
};

export function buildUrl(path: string, params?: Record<string, string | number>): string {
  let url = path;
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (url.includes(`:${key}`)) {
        url = url.replace(`:${key}`, String(value));
      }
    });
  }
  return url;
}
