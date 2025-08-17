// components/PostComposer.tsx
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { api } from '../lib/api';
import { Send, Sparkles } from 'lucide-react';

const postSchema = z.object({
  body: z.string()
    .min(1, 'Post cannot be empty')
    .max(140, 'Post must be 140 characters or less'),
});

type PostFormData = z.infer<typeof postSchema>;

interface PostComposerProps {
  onPost: () => void;
}

export default function PostComposer({ onPost }: PostComposerProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors },
  } = useForm<PostFormData>({
    resolver: zodResolver(postSchema),
  });

  const body = watch('body', '');
  const remaining = 140 - body.length;

  const onSubmit = async (data: PostFormData) => {
    setIsSubmitting(true);
    setError('');

    try {
      await api.createPost({ body: data.body });
      reset();
      onPost();
    } catch (error: any) {
      setError(error.message || 'Failed to create post');
    } finally {
      setIsSubmitting(false);
    }
  };

  const examples = [
    "Just finished a great workout! 💪",
    "Grateful for my morning coffee ☕",
    "Small win: organized my desk today!",
    "Beautiful sunset on my walk 🌅",
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
      <div className="flex items-center space-x-2 mb-4">
        <Sparkles className="h-5 w-5 text-pink-500" />
        <h2 className="text-lg font-medium text-gray-900">Share something positive!</h2>
      </div>
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <textarea
            {...register('body')}
            rows={4}
            className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent resize-none text-lg"
            placeholder="What made you smile today?"
          />
          
          <div className="flex justify-between items-center mt-3">
            <div className="text-sm text-gray-500">
              Keep it kind. Share a win, gratitude, or encouragement.
            </div>
            <div className={`text-sm font-medium ${remaining < 0 ? 'text-red-500' : remaining < 20 ? 'text-yellow-500' : 'text-gray-500'}`}>
              {remaining}
            </div>
          </div>
          
          {errors.body && (
            <p className="text-red-500 text-sm mt-2">{errors.body.message}</p>
          )}
          
          {error && (
            <p className="text-red-500 text-sm mt-2">{error}</p>
          )}
        </div>
        
        <div className="flex justify-between items-center">
          <div className="text-xs text-gray-400">
            <span className="font-medium">Examples:</span> {examples.join(' • ')}
          </div>
          
          <button
            type="submit"
            disabled={isSubmitting || remaining < 0 || !body.trim()}
            className="flex items-center space-x-2 bg-gradient-to-r from-pink-500 to-purple-600 text-white px-6 py-2 rounded-lg hover:from-pink-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <Send className="h-4 w-4" />
            <span>{isSubmitting ? 'Posting...' : 'Share'}</span>
          </button>
        </div>
      </form>
    </div>
  );
}