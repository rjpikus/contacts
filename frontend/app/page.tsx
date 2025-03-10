'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';

export default function Home() {
  const { isAuthenticated } = useAuthStore();
  const router = useRouter();
  
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/contacts');
    }
  }, [isAuthenticated, router]);
  
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh]">
      <h1 className="text-4xl font-bold mb-6">Welcome to Contacts App</h1>
      <p className="text-xl text-gray-600 mb-8 text-center max-w-2xl">
        A modern contact management system to organize and manage your contacts efficiently.
      </p>
      <div className="flex space-x-4">
        <button
          onClick={() => router.push('/auth/login')}
          className="bg-primary-500 text-white px-6 py-2 rounded-md hover:bg-primary-600 transition"
        >
          Login
        </button>
        <button
          onClick={() => router.push('/auth/register')}
          className="bg-white border border-primary-500 text-primary-500 px-6 py-2 rounded-md hover:bg-primary-50 transition"
        >
          Register
        </button>
      </div>
    </div>
  );
} 