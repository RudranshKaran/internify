import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Navbar from '@/components/Navbar'
import { Toast } from '@/components/Toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Internify - AI-Powered Internship Applications',
  description: 'Automate your internship applications with AI-generated personalized emails',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Navbar />
        <main className="min-h-screen bg-gray-50">
          {children}
        </main>
        <footer className="bg-white border-t border-gray-200 py-8">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-center items-center">
              <div className="flex space-x-6 text-sm">
                <a href="/privacy" className="text-gray-600 hover:text-primary transition-colors">
                  Privacy Policy
                </a>
                <a href="/terms" className="text-gray-600 hover:text-primary transition-colors">
                  Terms of Service
                </a>
              </div>
            </div>
          </div>
        </footer>
        <Toast />
      </body>
    </html>
  )
}
