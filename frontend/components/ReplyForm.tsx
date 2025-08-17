// components/ReplyForm.tsx
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { api } from '../lib/api';
import { Send } from 'lucide-react';

const replySchema = z.object({
  body: z.string()
    .min(1, 'Reply cannot be empty')
    .max(140, 'Reply must be 140 characters or less'),
});

type ReplyFormData = z.infer<typeof replySchema>;

interface ReplyFormProps {
  postId: string;
  onReply: () => void;
}

export default function ReplyForm({ postId, onReply }: ReplyFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors },
  } = useForm<ReplyFormData>({
    resolver: zodResolver(replySchema),
  });

  const body = watch('body', '');
  const remaining = 140 - body.length;

  const onSubmit = async (data: ReplyFormData) => {
    setIsSubmitting(true);
    setError('');

    try {
      await api.createPost({
        body: data.body,
        parent_id: postId,
      });
      reset();
      onReply();
    } catch (error: any) {
      setError(error.message || 'Failed to post reply');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3 mt-4 p-4 bg-gray-50 rounded-lg">
      <div>
        <textarea
          {...register('body')}
          rows={3}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent resize-none"
          placeholder="Share a positive reply..."
        />
        
        <div className="flex justify-between items-center mt-2">
          <div className="text-sm text-gray-500">
            Keep it positive! Share encouragement or gratitude.
          </div>
          <div className={`text-sm ${remaining < 0 ? 'text-red-500' : 'text-gray-500'}`}>
            {remaining}
          </div>
        </div>
        
        {errors.body && (
          <p className="text-red-500 text-sm mt-1">{errors.body.message}</p>
        )}
        
        {error && (
          <p className="text-red-500 text-sm mt-1">{error}</p>
        )}
      </div>
      
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isSubmitting || remaining < 0}
          className="flex items-center space-x-2 bg-pink-600 text-white px-4 py-2 rounded-lg hover:bg-pink-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send className="h-4 w-4" />
          <span>{isSubmitting ? 'Posting...' : 'Reply'}</span>
        </button>
      </div>
    </form>
  );
}