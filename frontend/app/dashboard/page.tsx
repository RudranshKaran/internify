'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabaseClient'
import { resumeAPI, jobsAPI } from '@/lib/api'
import { toast } from '@/components/Toast'
import ResumeUploader from '@/components/ResumeUploader'
import JobCard from '@/components/JobCard'
import Loader from '@/components/Loader'
import { Search } from 'lucide-react'

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [resume, setResume] = useState<any>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [jobs, setJobs] = useState<any[]>([])
  const [selectedJob, setSelectedJob] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [checking, setChecking] = useState(true)
  const hasCheckedAuth = useRef(false)
  const isRedirecting = useRef(false)

  useEffect(() => {
    // Only check auth once on mount
    if (hasCheckedAuth.current) return
    hasCheckedAuth.current = true
    checkAuth()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const checkAuth = async () => {
    try {
      // Add a delay to ensure session is fully available after redirect
      await new Promise(resolve => setTimeout(resolve, 200))
      
      const { data: { session } } = await supabase.auth.getSession()
      
      console.log('Dashboard: Checking auth, session:', session ? `exists (${session.user.email})` : 'none')
      
      if (!session && !isRedirecting.current) {
        console.log('Dashboard: No session found, redirecting to login')
        isRedirecting.current = true
        // No session, redirect to login with full page reload
        window.location.replace('/login')
        return
      }
      
      if (session) {
        console.log('Dashboard: Session validated, loading dashboard data')
        // Session exists, set user and fetch data
        setUser(session.user)
        setChecking(false)
        await fetchResume()
      }
    } catch (error) {
      console.error('Dashboard: Auth check error:', error)
      if (!isRedirecting.current) {
        isRedirecting.current = true
        window.location.replace('/login')
      }
    }
  }

  const fetchResume = async () => {
    try {
      const response = await resumeAPI.getLatest()
      if (response.data?.resume) {
        setResume(response.data.resume)
      }
    } catch (error) {
      // No resume yet
    }
  }

  const handleResumeUpload = async (file: File) => {
    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await resumeAPI.upload(formData)
      setResume(response.data)
      toast.success('Resume uploaded successfully!')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to upload resume')
    } finally {
      setUploading(false)
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchQuery.trim()) return

    setLoading(true)
    try {
      const response = await jobsAPI.search(searchQuery)
      setJobs(response.data.jobs || [])
      if (response.data.jobs?.length === 0) {
        toast.info('No jobs found. Try different keywords.')
      }
    } catch (error: any) {
      toast.error('Failed to search jobs')
    } finally {
      setLoading(false)
    }
  }

  const handleJobSelect = (job: any) => {
    setSelectedJob(job)
    // Store selected job in localStorage and navigate
    localStorage.setItem('selectedJob', JSON.stringify(job))
    localStorage.setItem('resumeText', resume?.extracted_text || '')
    router.push('/email-preview')
  }

  // Show loading while checking authentication
  if (checking) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader />
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

      {/* Resume Section */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">1. Upload Your Resume</h2>
        <ResumeUploader
          onUpload={handleResumeUpload}
          isUploading={uploading}
          uploadedFileName={resume?.file_path?.split('/').pop()}
        />
      </div>

      {/* Job Search Section */}
      {resume && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">2. Search for Jobs</h2>
          <form onSubmit={handleSearch} className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="e.g., Software Engineer Intern"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors font-medium disabled:opacity-50"
            >
              {loading ? 'Searching...' : 'Search Jobs'}
            </button>
          </form>
        </div>
      )}

      {/* Job Results */}
      {jobs.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">3. Select a Job</h2>
          {loading ? (
            <Loader text="Searching for jobs..." />
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {jobs.map((job, index) => (
                <JobCard
                  key={index}
                  job={job}
                  onSelect={handleJobSelect}
                  selected={selectedJob?.id === job.id}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {!resume && (
        <div className="text-center py-12 text-gray-500">
          <p>Upload your resume to start searching for jobs</p>
        </div>
      )}
    </div>
  )
}
