// components/PostCard.tsx
import React, { useState } from 'react';
import { Post } from '../types';
import { Heart, MessageCircle, Trash2 } from 'lucide-react';
import { api } from '../lib/api';
import { useAuth } from '../hooks/useAuth';

interface PostCardProps {
  post: Post;
  onUpdate?: () => void;
  showReplies?: boolean;
}

export default function PostCard({ post, onUpdate, showReplies = false }: PostCardProps): JSX.Element {
  const { user } = useAuth();
  const [isLiking, setIsLiking] = useState(false);
  const [likesCount, setLikesCount] = useState(post.like_count);
  const [userLiked, setUserLiked] = useState(post.user_liked);

  const handleLike = async (): Promise<void> => {
    if (!user || isLiking) return;
    
    setIsLiking(true);
    try {
      const result = await api.toggleLike(post.id);
      setLikesCount(result.like_count);
      setUserLiked(result.liked);
    } catch (error) {
      console.error('Failed to toggle like:', error);
    } finally {
      setIsLiking(false);
    }
  };

  const handleDelete = async (): Promise<void> => {
    if (!window.confirm('Are you sure you want to delete this post?')) return;
    
    try {
      await api.deletePost(post.id);
      onUpdate?.();
    } catch (error) {
      console.error('Failed to delete post:', error);
    }
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return React.createElement(
    'div',
    { className: 'bg-white rounded-lg shadow-sm border p-6 space-y-4' },
    React.createElement(
      'div',
      { className: 'flex items-start justify-between' },
      React.createElement(
        'div',
        { className: 'flex-1' },
        post.author ? React.createElement(
          'div',
          { className: 'flex items-center space-x-2 mb-2' },
          React.createElement('span', { className: 'font-medium text-gray-900' }, post.author.display_name),
          React.createElement('span', { className: 'text-gray-500 text-sm' }, `@${post.author.handle}`),
          React.createElement('span', { className: 'text-gray-400 text-sm' }, '·'),
          React.createElement('span', { className: 'text-gray-500 text-sm' }, formatDate(post.created_at))
        ) : React.createElement(
          'div',
          { className: 'mb-2 text-gray-500 text-sm' },
          `[Post removed by author] · ${formatDate(post.created_at)}`
        ),
        React.createElement('p', { className: 'text-gray-800 leading-relaxed' }, post.body)
      ),
      user && post.author && user.id === post.author.id && React.createElement(
        'button',
        {
          onClick: handleDelete,
          className: 'text-gray-400 hover:text-red-500 p-1'
        },
        React.createElement(Trash2, { className: 'h-4 w-4' })
      )
    ),
    React.createElement(
      'div',
      { className: 'flex items-center justify-between pt-2 border-t' },
      React.createElement(
        'div',
        { className: 'flex items-center space-x-6' },
        React.createElement(
          'button',
          {
            onClick: handleLike,
            disabled: !user || isLiking,
            className: `flex items-center space-x-2 text-sm ${
              userLiked 
                ? 'text-pink-600' 
                : 'text-gray-500 hover:text-pink-600'
            } disabled:opacity-50`
          },
          React.createElement(Heart, { className: `h-5 w-5 ${userLiked ? 'fill-current' : ''}` }),
          React.createElement('span', null, likesCount)
        ),
        showReplies && React.createElement(
          'div',
          { className: 'flex items-center space-x-2 text-sm text-gray-500' },
          React.createElement(MessageCircle, { className: 'h-5 w-5' }),
          React.createElement('span', null, post.reply_count)
        )
      )
    )
  );
}