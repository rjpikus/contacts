'use client';

import './globals.css';
import { Inter } from 'next/font/google';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { useAuthStore } from '@/lib/store';
import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';

const inter = Inter({ subsets: ['latin'] });

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, user, checkAuth, logout } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();
  
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);
  
  // Public routes that don't require authentication
  const publicRoutes = ['/', '/auth/login', '/auth/register'];
  
  useEffect(() => {
    if (!isAuthenticated && !publicRoutes.includes(pathname)) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, pathname, router]);
  
  const handleLogout = () => {
    logout();
    router.push('/auth/login');
  };
  
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex flex-col min-h-screen">
          <header className="bg-primary-500 text-white shadow-md">
            <div className="container mx-auto px-4 py-4">
              <div className="flex justify-between items-center">
                <Link href="/" className="text-2xl font-bold">
                  Contacts App
                </Link>
                
                {isAuthenticated ? (
                  <nav className="flex items-center space-x-6">
                    <Link href="/contacts" className="hover:text-primary-200">
                      Contacts
                    </Link>
                    <Link href="/groups" className="hover:text-primary-200">
                      Groups
                    </Link>
                    <div className="flex items-center space-x-4">
                      <span>{user?.email}</span>
                      <button 
                        onClick={handleLogout}
                        className="bg-white text-primary-500 px-3 py-1 rounded hover:bg-primary-100"
                      >
                        Logout
                      </button>
                    </div>
                  </nav>
                ) : (
                  <nav className="flex space-x-4">
                    <Link href="/auth/login" className="hover:text-primary-200">
                      Login
                    </Link>
                    <Link href="/auth/register" className="hover:text-primary-200">
                      Register
                    </Link>
                  </nav>
                )}
              </div>
            </div>
          </header>
          
          <main className="flex-grow container mx-auto px-4 py-8">
            {children}
          </main>
          
          <footer className="bg-gray-100 py-6">
            <div className="container mx-auto px-4 text-center text-gray-500">
              <p>&copy; {new Date().getFullYear()} Contacts App. All rights reserved.</p>
            </div>
          </footer>
        </div>
        
        <ToastContainer position="bottom-right" />
      </body>
    </html>
  );
} 