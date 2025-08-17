// pages/index.tsx
import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import PostComposer from '../components/PostComposer';
import PostCard from '../components/PostCard';
import { api } from '../lib/api';
import { Post } from '../types';
import { Loader2 } from 'lucide-react';
import Link from 'next/link';

export default function Home() {
  const { user, loading: authLoading } = useAuth();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    loadPosts();
  }, []);

  const loadPosts = async (cursor?: string) => {
    try {
      setError('');
      if (cursor) {
        setLoadingMore(true);
      } else {
        setLoading(true);
      }

      const data = await api.getPosts(cursor);
      
      if (cursor) {
        setPosts(prev => [...prev, ...data.items]);
      } else {
        setPosts(data.items);
      }
      
      setNextCursor(data.next_cursor);
    } catch (error: any) {
      setError(error.message || 'Failed to load posts');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const handleNewPost = () => {
    loadPosts(); // Reload from beginning
  };

  const handlePostUpdate = () => {
    loadPosts(); // Reload from beginning
  };

  if (authLoading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <Loader2 className="h-8 w-8 animate-spin text-pink-500" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="text-center py-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Welcome to Positive Journal
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          A place to share small wins, gratitude, and positive moments.
        </p>
        <div className="space-x-4">
          <Link
            href="/login"
            className="bg-pink-600 text-white px-6 py-3 rounded-lg hover:bg-pink-700 transition-colors"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="border border-pink-600 text-pink-600 px-6 py-3 rounded-lg hover:bg-pink-50 transition-colors"
          >
            Sign Up
          </Link>
        </div>
        
        {!loading && posts.length > 0 && (
          <div className="mt-12">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">
              Recent positive posts
            </h2>
            <div className="space-y-4">
              {posts.slice(0, 3).map((post) => (
                <PostCard key={post.id} post={post} />
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div>
      <PostComposer onPost={handleNewPost} />
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}
      
      {loading ? (
        <div className="flex justify-center items-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-pink-500" />
        </div>
      ) : (
        <div className="space-y-6">
          {posts.map((post) => (
            <PostCard
              key={post.id}
              post={post}
              onUpdate={handlePostUpdate}
              showReplies={true}
            />
          ))}
          
          {posts.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <p className="text-lg">No posts yet!</p>
              <p>Be the first to share something positive.</p>
            </div>
          )}
          
          {nextCursor && (
            <div className="text-center py-6">
              <button
                onClick={() => loadPosts(nextCursor)}
                disabled={loadingMore}
                className="bg-gray-100 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-200 disabled:opacity-50"
              >
                {loadingMore ? (
                  <span className="flex items-center space-x-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Loading...</span>
                  </span>
                ) : (
                  'Load More'
                )}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}