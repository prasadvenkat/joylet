// pages/p/[id].tsx
import { useRouter } from 'next/router';
import { useState, useEffect } from 'react';
import { api } from '../../lib/api';
import { PostDetail } from '../../types';
import PostCard from '../../components/PostCard';
import ReplyForm from '../../components/ReplyForm';
import { useAuth } from '../../hooks/useAuth';
import { Loader2, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function PostDetailPage() {
  const router = useRouter();
  const { id } = router.query;
  const { user } = useAuth();
  const [postDetail, setPostDetail] = useState<PostDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (id && typeof id === 'string') {
      loadPost();
    }
  }, [id]);

  const loadPost = async () => {
    if (!id || typeof id !== 'string') return;

    try {
      setError('');
      setLoading(true);
      const data = await api.getPost(id);
      setPostDetail(data);
    } catch (error: any) {
      setError(error.message || 'Failed to load post');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <Loader2 className="h-8 w-8 animate-spin text-pink-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg inline-block">
          {error}
        </div>
        <div className="mt-4">
          <Link href="/" className="text-pink-600 hover:text-pink-700">
            ← Back to feed
          </Link>
        </div>
      </div>
    );
  }

  if (!postDetail) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Post not found</p>
        <Link href="/" className="text-pink-600 hover:text-pink-700 mt-2 inline-block">
          ← Back to feed
        </Link>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <Link href="/" className="flex items-center space-x-2 text-gray-600 hover:text-gray-800">
          <ArrowLeft className="h-4 w-4" />
          <span>Back to feed</span>
        </Link>
      </div>

      <div className="space-y-6">
        <PostCard post={postDetail.post} onUpdate={loadPost} />

        {user && (
          <div className="ml-8">
            <ReplyForm postId={postDetail.post.id} onReply={loadPost} />
          </div>
        )}

        {postDetail.replies.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 ml-8">
              Replies ({postDetail.replies.length})
            </h3>
            {postDetail.replies.map((reply) => (
              <div key={reply.id} className="ml-8">
                <PostCard post={reply} onUpdate={loadPost} />
              </div>
            ))}
          </div>
        )}

        {postDetail.replies.length === 0 && user && (
          <div className="text-center py-8 text-gray-500 ml-8">
            <p>No replies yet. Be the first to share encouragement!</p>
          </div>
        )}
      </div>
    </div>
  );
}