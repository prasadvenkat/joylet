import React, { ReactNode } from 'react';
import { useAuth } from '../hooks/useAuth';
import { Heart, LogOut, User } from 'lucide-react';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps): JSX.Element {
  const { user, logout } = useAuth();

  return React.createElement(
    'div',
    { className: 'min-h-screen bg-gradient-to-br from-pink-50 to-purple-50' },
    React.createElement(
      'header',
      { className: 'bg-white shadow-sm border-b' },
      React.createElement(
        'div',
        { className: 'max-w-4xl mx-auto px-4 sm:px-6 lg:px-8' },
        React.createElement(
          'div',
          { className: 'flex justify-between items-center h-16' },
          React.createElement(
            'div',
            { className: 'flex items-center space-x-2' },
            React.createElement(Heart, { className: 'h-8 w-8 text-pink-500' }),
            React.createElement('h1', { className: 'text-xl font-bold text-gray-900' }, 'Positive Journal')
          ),
          user && React.createElement(
            'div',
            { className: 'flex items-center space-x-4' },
            React.createElement(
              'div',
              { className: 'flex items-center space-x-2' },
              React.createElement(User, { className: 'h-5 w-5 text-gray-500' }),
              React.createElement('span', { className: 'text-sm text-gray-700' }, user.display_name)
            ),
            React.createElement(
              'button',
              {
                onClick: logout,
                className: 'flex items-center space-x-1 text-sm text-gray-500 hover:text-gray-700'
              },
              React.createElement(LogOut, { className: 'h-4 w-4' }),
              React.createElement('span', null, 'Logout')
            )
          )
        )
      )
    ),
    React.createElement(
      'main',
      { className: 'max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8' },
      children
    )
  );
}