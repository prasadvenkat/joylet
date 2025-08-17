// components/PostComposer.tsx
import React, { useState } from 'react';
import { api } from '../lib/api';
import { Send, Sparkles } from 'lucide-react';

interface PostComposerProps {
  onPost: () => void;
}

export default function PostComposer({ onPost }: PostComposerProps): JSX.Element {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [body, setBody] = useState('');

  const remaining = 140 - body.length;

  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    if (!body.trim() || remaining < 0) return;

    setIsSubmitting(true);
    setError('');

    try {
      await api.createPost({ body });
      setBody('');
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

  return React.createElement(
    'div',
    { className: 'bg-white rounded-lg shadow-sm border p-6 mb-6' },
    React.createElement(
      'div',
      { className: 'flex items-center space-x-2 mb-4' },
      React.createElement(Sparkles, { className: 'h-5 w-5 text-pink-500' }),
      React.createElement('h2', { className: 'text-lg font-medium text-gray-900' }, 'Share something positive!')
    ),
    React.createElement(
      'form',
      { onSubmit: handleSubmit, className: 'space-y-4' },
      React.createElement(
        'div',
        null,
        React.createElement('textarea', {
          value: body,
          onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => setBody(e.target.value),
          rows: 4,
          className: 'w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent resize-none text-lg',
          placeholder: 'What made you smile today?'
        }),
        React.createElement(
          'div',
          { className: 'flex justify-between items-center mt-3' },
          React.createElement(
            'div',
            { className: 'text-sm text-gray-500' },
            'Keep it kind. Share a win, gratitude, or encouragement.'
          ),
          React.createElement(
            'div',
            { className: `text-sm font-medium ${remaining < 0 ? 'text-red-500' : remaining < 20 ? 'text-yellow-500' : 'text-gray-500'}` },
            remaining
          )
        ),
        error && React.createElement(
          'p',
          { className: 'text-red-500 text-sm mt-2' },
          error
        )
      ),
      React.createElement(
        'div',
        { className: 'flex justify-between items-center' },
        React.createElement(
          'div',
          { className: 'text-xs text-gray-400' },
          React.createElement('span', { className: 'font-medium' }, 'Examples: '),
          examples.join(' • ')
        ),
        React.createElement(
          'button',
          {
            type: 'submit',
            disabled: isSubmitting || remaining < 0 || !body.trim(),
            className: 'flex items-center space-x-2 bg-gradient-to-r from-pink-500 to-purple-600 text-white px-6 py-2 rounded-lg hover:from-pink-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all'
          },
          React.createElement(Send, { className: 'h-4 w-4' }),
          React.createElement('span', null, isSubmitting ? 'Posting...' : 'Share')
        )
      )
    )
  );
}