'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabaseClient'
import { llmAPI, emailAPI } from '@/lib/api'
import { toast } from '@/components/Toast'
import EmailPreview from '@/components/EmailPreview'
import Loader from '@/components/Loader'
import { ArrowLeft, RefreshCw } from 'lucide-react'
import Link from 'next/link'

export default function EmailPreviewPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [sending, setSending] = useState(false)
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')
  const [job, setJob] = useState<any>(null)
  const [recipientEmail, setRecipientEmail] = useState('')
  const hasCheckedAuth = useRef(false)
  const isRedirecting = useRef(false)

  useEffect(() => {
    if (hasCheckedAuth.current) return
    hasCheckedAuth.current = true
    checkAuthAndGenerate()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const checkAuthAndGenerate = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) {
      window.location.replace('/login')
      return
    }

    // Get job from localStorage
    const jobData = localStorage.getItem('selectedJob')
    const resumeText = localStorage.getItem('resumeText')

    if (!jobData) {
      toast.error('No job selected')
      router.push('/dashboard')
      return
    }

    const parsedJob = JSON.parse(jobData)
    setJob(parsedJob)

    // Extract recipient email (you might need to implement email extraction logic)
    const email = extractEmailFromJob(parsedJob)
    setRecipientEmail(email)

    // Generate email
    await generateEmail(parsedJob, resumeText || '')
  }

  const extractEmailFromJob = (job: any): string => {
    // Simple extraction - in real app, you'd need better logic
    // For now, use a placeholder
    return job.company ? `hr@${job.company.toLowerCase().replace(/\s+/g, '')}.com` : 'contact@company.com'
  }

  const generateEmail = async (jobData: any, resumeText: string) => {
    setGenerating(true)
    try {
      const response = await llmAPI.generateEmail({
        job_description: jobData.description || jobData.title,
        resume_text: resumeText,
        job_title: jobData.title,
        company_name: jobData.company,
      })

      setSubject(response.data.subject)
      setBody(response.data.body)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to generate email')
      router.push('/dashboard')
    } finally {
      setGenerating(false)
      setLoading(false)
    }
  }

  const handleRegenerate = async () => {
    if (!job) return
    const resumeText = localStorage.getItem('resumeText') || ''
    await generateEmail(job, resumeText)
  }

  const handleSend = async () => {
    setSending(true)
    try {
      await emailAPI.send({
        job_id: job.id,
        recipient_email: recipientEmail,
        subject,
        body,
      })

      toast.success('Email sent successfully!')
      router.push('/history')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to send email')
    } finally {
      setSending(false)
    }
  }

  if (loading || generating) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20">
        <Loader text={generating ? 'Generating personalized email...' : 'Loading...'} />
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6 flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center text-gray-600 hover:text-gray-900">
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Dashboard
        </Link>
        <button
          onClick={handleRegenerate}
          disabled={generating}
          className="flex items-center space-x-2 px-4 py-2 text-primary hover:bg-primary/10 rounded-lg transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
          <span>Regenerate</span>
        </button>
      </div>

      <h1 className="text-3xl font-bold text-gray-900 mb-2">Email Preview</h1>
      <p className="text-gray-600 mb-8">
        Review and customize your AI-generated email before sending
      </p>

      {job && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold text-gray-900">{job.title}</h3>
          <p className="text-sm text-gray-600">{job.company}</p>
        </div>
      )}

      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Recipient Email
        </label>
        <input
          type="email"
          value={recipientEmail}
          onChange={(e) => setRecipientEmail(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
          placeholder="hr@company.com"
        />
      </div>

      <EmailPreview
        subject={subject}
        body={body}
        recipientEmail={recipientEmail}
        onSubjectChange={setSubject}
        onBodyChange={setBody}
        onSend={handleSend}
        isSending={sending}
      />
    </div>
  )
}
