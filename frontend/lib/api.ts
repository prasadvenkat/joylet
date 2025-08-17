import { User, PublicUser, PostList, PostDetail } from '../types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi(endpoint: string, options: RequestInit = {}) {
  const url = `${API_URL}${endpoint}`;
  
  const response = await fetch(url, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Unknown error' }));
    throw new ApiError(response.status, error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Auth
  register: (data: { email: string; password: string; display_name: string }) =>
    fetchApi('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  login: (data: { email: string; password: string }) =>
    fetchApi('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  logout: () =>
    fetchApi('/auth/logout', {
      method: 'POST',
    }),

  verifyEmail: (token: string) =>
    fetchApi('/auth/verify-email', {
      method: 'POST',
      body: JSON.stringify({ token }),
    }),

  // Users
  getMe: (): Promise<User> => fetchApi('/users/me'),

  getUser: (userId: string): Promise<PublicUser> => fetchApi(`/users/${userId}`),

  // Posts
  getPosts: (cursor?: string, limit = 20): Promise<PostList> => {
    const params = new URLSearchParams();
    if (cursor) params.append('cursor', cursor);
    params.append('limit', limit.toString());
    return fetchApi(`/posts?${params}`);
  },

  createPost: (data: { body: string; parent_id?: string }) =>
    fetchApi('/posts', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getPost: (postId: string): Promise<PostDetail> =>
    fetchApi(`/posts/${postId}`),

  deletePost: (postId: string) =>
    fetchApi(`/posts/${postId}`, {
      method: 'DELETE',
    }),

  // Likes
  toggleLike: (postId: string) =>
    fetchApi(`/posts/${postId}/like`, {
      method: 'POST',
    }),
};