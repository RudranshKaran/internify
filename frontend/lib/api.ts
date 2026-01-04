import axios from 'axios'
import { supabase } from './supabaseClient'

const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: backendUrl,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    try {
      // Get current session token
      const { data: { session } } = await supabase.auth.getSession()
      
      console.log('API: Attaching auth token for request:', config.url, session ? 'token found' : 'no token')
      
      if (session?.access_token) {
        config.headers.Authorization = `Bearer ${session.access_token}`
        console.log('API: Authorization header set with token length:', session.access_token.length)
      } else {
        console.warn('API: No session found, making unauthenticated request')
      }
    } catch (error) {
      console.error('API: Error getting auth token:', error)
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Log the error for debugging
    console.error('API Error:', error.response?.status, error.response?.data, error.config?.url)
    
    // Only redirect to login on 401 if we're not already on the login page
    // AND only if it's not a "no resume found" type error
    if (error.response?.status === 401) {
      const isResumeEndpoint = error.config?.url?.includes('/resume')
      const isJobEndpoint = error.config?.url?.includes('/jobs')
      
      // Don't redirect for resource not found - user might just not have data yet
      if (isResumeEndpoint || isJobEndpoint) {
        console.log('API: 401 on data endpoint - user may not have uploaded data yet')
        return Promise.reject(error)
      }
      
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        console.error('API: Authentication failed, redirecting to login')
        // Clear any stale session data
        await supabase.auth.signOut()
        window.location.href = '/login'
      }
    }
    
    return Promise.reject(error)
  }
)

export default api

// API endpoints
export const authAPI = {
  verify: () => api.post('/auth/verify'),
  getMe: () => api.get('/auth/me'),
}

export const resumeAPI = {
  upload: (formData: FormData) => api.post('/resume/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getLatest: () => api.get('/resume/latest'),
  delete: (resumeId: string) => api.delete(`/resume/${resumeId}`),
}

export const internshipsAPI = {
  search: (role: string, location?: string, limit?: number) => 
    api.get('/internships/search', { params: { role, location, limit } }),
  getById: (internshipId: string) => api.get(`/internships/${internshipId}`),
  searchByCompany: (companyName: string, role?: string) =>
    api.get(`/internships/company/${companyName}`, { params: { role } }),
}

export const llmAPI = {
  generateEmail: (data: {
    internship_description: string
    resume_text: string
    internship_title: string
    company_name: string
  }) => api.post('/llm/generate-email', data),
  regenerateEmail: (data: any) => api.post('/llm/regenerate-email', data),
}

export const emailAPI = {
  send: (data: {
    internship_id: string
    recipient_email: string
    subject: string
    body: string
  }) => api.post('/email/send', data),
  getHistory: (limit?: number) => api.get('/email/history', { params: { limit } }),
  getById: (emailId: string) => api.get(`/email/${emailId}`),
  delete: (emailId: string) => api.delete(`/email/${emailId}`),
}
