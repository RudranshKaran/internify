'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabaseClient'
import { resumeAPI, internshipsAPI } from '@/lib/api'
import { toast } from '@/components/Toast'
import ResumeUploader from '@/components/ResumeUploader'
import InternshipCard from '@/components/InternshipCard'
import Loader from '@/components/Loader'
import SearchLoading from '@/components/SearchLoading'
import { Search } from 'lucide-react'

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [resume, setResume] = useState<any>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [internships, setInternships] = useState<any[]>([])
  const [selectedInternship, setSelectedInternship] = useState<any>(null)
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
        
        // Restore saved search results from sessionStorage so navigating back
        // from email-preview keeps the list intact
        const savedInternships = sessionStorage.getItem('dashboardInternships')
        if (savedInternships) {
          try {
            const parsed = JSON.parse(savedInternships)
            if (Array.isArray(parsed) && parsed.length > 0) {
              setInternships(parsed)
            }
          } catch {}
        }
        
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
      console.log('Dashboard: Backend URL:', process.env.NEXT_PUBLIC_BACKEND_URL)
      
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
      console.error('Dashboard: Request URL:', error.config?.url)
      console.error('Dashboard: Request method:', error.config?.method)
      
      let errorMessage = 'Failed to upload resume'
      
      if (error.response?.status === 405) {
        errorMessage = 'Upload endpoint not found. Please check backend configuration.'
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail
      } else if (error.message) {
        errorMessage = error.message
      }
      
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
    setInternships([])

    try {
      // ── Phase 1: trigger background discovery ──
      console.log('Dashboard: Triggering search for:', searchQuery)
      const triggerRes = await internshipsAPI.search(searchQuery)
      console.log('Dashboard: Search triggered:', triggerRes.data)

      // ── Phase 2: fetch stored companies ──
      // Give the background task a moment to start writing, then grab the
      // first page of results from the discovered_companies table.
      console.log('Dashboard: Fetching discovered companies…')
      const listRes = await internshipsAPI.listDiscovered({ limit: 50 })
      console.log('Dashboard: Companies response:', listRes.data)

      // Safely extract companies — the shape changed from
      // { internships: […] } to { companies: […] }.
      const companies: any[] =
        listRes.data?.companies ?? listRes.data?.internships ?? []

      // Map discovered_companies fields to what InternshipCard expects
      const mapped = companies.map((c: any) => ({
        id: c.id,
        title: c.role_title || '',
        company: c.company_name || '',
        location: c.location || '',
        description: c.job_description_snippet || '',
        link: c.source_url || '',
        // The rest are empty for now (enriched later)
        posted_at: c.last_seen_at || c.discovered_at,
        contact_email: undefined,
        contact_phone: undefined,
        contact_website: undefined,
        domain: c.domain,
        email_status: c.email_status,
      }))

      setInternships(mapped)

      // Save to sessionStorage so results persist when navigating back from email-preview
      if (mapped.length > 0) {
        sessionStorage.setItem('dashboardInternships', JSON.stringify(mapped))
      }

      if (mapped.length === 0) {
        toast.info(
          'Search is running in the background. Results will appear here once companies are discovered. Try searching again in a moment.'
        )
      } else {
        toast.success(`Found ${mapped.length} companies!`)
      }
    } catch (error: any) {
      console.error('Dashboard: Search error:', error)
      // Guard against TypeError (e.g. reading .data on undefined) that
      // doesn't carry a .response property — those are client-side bugs,
      // not network failures.
      const isClientError = !error.response
      const errorMessage = isClientError
        ? 'Something went wrong processing the search results. Please try again.'
        : error.response?.data?.detail || error.message || 'Failed to search internships'
      toast.error(errorMessage)
      setInternships([])
    } finally {
      setLoading(false)
    }
  }

  const handleInternshipSelect = (internship: any) => {
    console.log('[DASHBOARD] Selected internship:', internship.title)
    console.log('[DASHBOARD] Company:', internship.company)
    console.log('[DASHBOARD] Description length:', internship.description?.length || 0, 'chars')
    console.log('[DASHBOARD] Description preview:', internship.description?.substring(0, 200) || 'NO DESCRIPTION')
    
    setSelectedInternship(internship)
    // Store selected internship in localStorage and navigate
    localStorage.setItem('selectedInternship', JSON.stringify(internship))
    router.push('/email-preview')
  }

  const handleResumeDelete = async () => {
    if (!resume?.id) {
      toast.error('No resume to delete')
      return
    }

    try {
      console.log('Dashboard: Deleting resume:', resume.id)
      await resumeAPI.delete(resume.id)
      setResume(null)
      setInternships([]) // Clear internship results
      setSelectedInternship(null)
      toast.success('Resume deleted successfully!')
    } catch (error: any) {
      console.error('Dashboard: Resume delete failed:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to delete resume'
      toast.error(errorMessage)
    }
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
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pb-24">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

      {/* Resume Section */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">1. Upload Your Resume</h2>
        <ResumeUploader
          onUpload={handleResumeUpload}
          onDelete={handleResumeDelete}
          isUploading={uploading}
          uploadedFileName={resume?.file_path?.split('/').pop()}
        />
      </div>

      {/* Internship Search Section */}
      {resume && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">2. Search for Internships</h2>
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
              {loading ? 'Searching...' : 'Search Internships'}
            </button>
          </form>
        </div>
      )}

      {/* Internship Results — visible during loading too so the spinner shows */}
      {(loading || internships.length > 0) && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">3. Select an Internship to Apply</h2>
            {selectedInternship && !loading && (
              <button
                onClick={() => handleInternshipSelect(selectedInternship)}
                className="px-6 py-3 bg-gradient-to-r from-primary to-blue-600 text-white rounded-lg hover:opacity-90 transition-all font-medium shadow-md hover:shadow-lg flex items-center gap-2"
              >
                <span>Generate Email</span>
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </button>
            )}
          </div>
          {loading ? (
            <SearchLoading />
          ) : internships.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              No companies found yet. Try a different search term.
            </p>
          ) : (
            <>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {internships.map((internship, index) => (
                  <InternshipCard
                    key={index}
                    internship={internship}
                    onSelect={setSelectedInternship}
                    selected={selectedInternship?.title === internship.title && selectedInternship?.company === internship.company}
                  />
                ))}
              </div>
              {selectedInternship && (
                <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                      <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">Internship Selected: {selectedInternship.title}</p>
                      <p className="text-sm text-gray-600">at {selectedInternship.company}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleInternshipSelect(selectedInternship)}
                    className="px-5 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
                  >
                    Continue →
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {!resume && (
        <div className="text-center py-12 text-gray-500">
          <p>Upload your resume to start searching for internships</p>
        </div>
      )}

      {/* Floating bottom bar with Generate Email button */}
      {selectedInternship && !loading && (
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-[0_-4px_12px_rgba(0,0,0,0.08)] z-50 px-4 py-3">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-3 min-w-0">
              <div className="w-2 h-2 rounded-full bg-green-500 shrink-0" />
              <p className="text-sm text-gray-700 truncate">
                <span className="font-medium">{selectedInternship.title}</span>
                <span className="text-gray-500"> at </span>
                <span>{selectedInternship.company}</span>
              </p>
            </div>
            <button
              onClick={() => handleInternshipSelect(selectedInternship)}
              className="shrink-0 px-6 py-2.5 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors font-medium flex items-center gap-2 shadow-sm"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <span>Generate Email</span>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
