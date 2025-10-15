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
    
    const checkAuth = async () => {
      try {
        console.log('Dashboard: Starting auth check...')
        
        // Use getUser() instead of getSession() - it's more reliable and validates the JWT
        const { data: { user }, error } = await supabase.auth.getUser()
        
        console.log('Dashboard: Checking auth, user:', user ? `exists (${user.email})` : 'none', error ? `error: ${error.message}` : '')
        
        if (error || !user) {
          if (!isRedirecting.current) {
            console.log('Dashboard: No valid user found, redirecting to login')
            isRedirecting.current = true
            // No user, redirect to login with full page reload
            window.location.replace('/login')
          }
          return
        }
        
        if (user) {
          console.log('Dashboard: User validated, loading dashboard data')
          // User exists, set user and fetch data
          setUser(user)
          setChecking(false)
          
          // Wait a bit before calling backend API to ensure token is ready
          setTimeout(() => {
            fetchResume()
          }, 500)
        }
      } catch (error) {
        console.error('Dashboard: Auth check error:', error)
        if (!isRedirecting.current) {
          isRedirecting.current = true
          window.location.replace('/login')
        }
      }
    }

    checkAuth()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const fetchResume = async () => {
    try {
      console.log('Dashboard: Fetching resume from backend...')
      const response = await resumeAPI.getLatest()
      console.log('Dashboard: Resume fetch successful', response.data)
      if (response.data?.resume) {
        setResume(response.data.resume)
      }
    } catch (error: any) {
      // No resume yet - this is fine for new users
      console.log('Dashboard: No resume found (this is normal for new users)', error.message)
      // Don't let resume fetch errors redirect - user might just not have uploaded yet
    }
  }

  const handleResumeUpload = async (file: File) => {
    setUploading(true)
    try {
      console.log('Dashboard: Uploading resume file:', file.name, file.size, 'bytes')
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await resumeAPI.upload(formData)
      console.log('Dashboard: Resume upload successful:', response.data)
      setResume(response.data)
      toast.success('Resume uploaded successfully!')
    } catch (error: any) {
      console.error('Dashboard: Resume upload failed:', error)
      console.error('Dashboard: Error response:', error.response?.data)
      console.error('Dashboard: Error status:', error.response?.status)
      
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to upload resume'
      toast.error(errorMessage)
      
      // If it's an auth error, don't let the interceptor handle it
      if (error.response?.status === 401) {
        console.error('Dashboard: Authentication error during upload. Token may be invalid.')
      }
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
