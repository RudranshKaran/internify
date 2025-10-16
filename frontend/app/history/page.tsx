'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabaseClient'
import { emailAPI } from '@/lib/api'
import { toast } from '@/components/Toast'
import Loader from '@/components/Loader'
import { Mail, Calendar, Building, ExternalLink } from 'lucide-react'
import { formatDateTime } from '@/lib/utils'

export default function HistoryPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [emails, setEmails] = useState<any[]>([])
  const hasCheckedAuth = useRef(false)
  const isRedirecting = useRef(false)

  useEffect(() => {
    if (hasCheckedAuth.current) return
    hasCheckedAuth.current = true
    checkAuthAndFetch()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const checkAuthAndFetch = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) {
      window.location.replace('/login')
      return
    }
    await fetchEmails()
  }

  const fetchEmails = async () => {
    setLoading(true)
    try {
      const response = await emailAPI.getHistory(50)
      setEmails(response.data.emails || [])
    } catch (error: any) {
      toast.error('Failed to fetch email history')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20">
        <Loader text="Loading email history..." />
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Email History</h1>
        <p className="text-gray-600">
          View all your sent applications ({emails.length} total)
        </p>
      </div>

      {emails.length === 0 ? (
        <div className="text-center py-20">
          <Mail className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No emails sent yet</h2>
          <p className="text-gray-600 mb-6">
            Start applying to internships from your dashboard
          </p>
          <button
            onClick={() => router.push('/dashboard')}
            className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors font-medium"
          >
            Go to Dashboard
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {emails.map((email) => (
            <div
              key={email.id}
              className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {email.subject}
                  </h3>
                  <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                    {email.internships && (
                      <div className="flex items-center">
                        <Building className="w-4 h-4 mr-1" />
                        <span>{email.internships.company}</span>
                      </div>
                    )}
                    <div className="flex items-center">
                      <Calendar className="w-4 h-4 mr-1" />
                      <span>{formatDateTime(email.sent_at)}</span>
                    </div>
                    <div className="flex items-center">
                      <Mail className="w-4 h-4 mr-1" />
                      <span>{email.recipient_email}</span>
                    </div>
                  </div>
                </div>
                <div className="flex-shrink-0">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    {email.status}
                  </span>
                </div>
              </div>

              <div className="text-sm text-gray-700 line-clamp-3 mb-4">
                {email.body}
              </div>

              {email.internships?.link && (
                <a
                  href={email.internships.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-primary hover:text-primary/80 text-sm font-medium"
                >
                  View Internship Posting
                  <ExternalLink className="w-3 h-3 ml-1" />
                </a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
