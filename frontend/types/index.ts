export interface User {
  id: string;
  email: string;
  display_name: string;
  handle: string;
  created_at: string;
}

export interface PublicUser {
  id: string;
  display_name: string;
  handle: string;
  created_at: string;
  post_count: number;
}

export interface Post {
  id: string;
  body: string;
  author: {
    id: string;
    display_name: string;
    handle: string;
  } | null;
  parent_id: string | null;
  like_count: number;
  reply_count: number;
  user_liked: boolean;
  created_at: string;
}

export interface PostList {
  items: Post[];
  next_cursor: string | null;
}

export interface PostDetail {
  post: Post;
  replies: Post[];
}