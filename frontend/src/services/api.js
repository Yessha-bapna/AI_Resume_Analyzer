import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'https://ai-resume-analyzer-l70u.onrender.com/api',
  headers: {
    'Content-Type': 'application/json',
  }
})

// Request interceptor - cookies are automatically sent with requests
api.interceptors.request.use(
  (config) => {
    // Cookies are automatically sent by the browser, no need to manually set headers
    config.withCredentials = true  // Ensure cookies are sent with requests
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Don't redirect for auth endpoints (login, register)
      const authEndpoints = ['/auth/login', '/auth/register']
      const isAuthEndpoint = authEndpoints.some(endpoint => 
        error.config?.url?.includes(endpoint)
      )
      
      if (!isAuthEndpoint) {
        // Only redirect if not already on login page
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: (userData) => api.put('/auth/update-profile', userData),
}

// Jobs API
export const jobsAPI = {
  getJobs: (params) => api.get('/jobs', { params }),
  getJob: (id) => api.get(`/jobs/${id}`),
  createJob: (jobData) => {
    // Check if jobData is FormData (for file uploads)
    if (jobData instanceof FormData) {
      return api.post('/jobs', jobData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    return api.post('/jobs', jobData)
  },
  updateJob: (id, jobData) => api.put(`/jobs/${id}`, jobData),
  deleteJob: (id) => api.delete(`/jobs/${id}`),
}

// Resumes API
export const resumesAPI = {
  uploadResume: (formData) => api.post('/resumes/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getResumes: (params) => api.get('/resumes', { params }),
  getResume: (id) => api.get(`/resumes/${id}`),
  deleteResume: (id) => api.delete(`/resumes/${id}`),
  analyzeResume: (resumeId, jobId) => api.post(`/resumes/analyze/${resumeId}/${jobId}`),
  getAnalyses: (params) => api.get('/resumes/analyses', { params }),
}

// Applications API
export const applicationsAPI = {
  applyForJob: (applicationData) => api.post('/applications', applicationData),
  getApplications: (params) => api.get('/applications', { params }),
  getApplication: (id) => api.get(`/applications/${id}`),
  withdrawApplication: (id) => api.delete(`/applications/${id}`),
}

// Admin API
export const adminAPI = {
  getDashboard: () => api.get('/admin/dashboard'),
  getJobRankings: (jobId) => api.get(`/admin/jobs/${jobId}/rankings`),
  getQueueStatus: (jobId) => api.get(`/admin/jobs/${jobId}/queue-status`),
  getAllAnalyses: (params) => api.get('/admin/analyses', { params }),
  getUsers: (params) => api.get('/admin/users', { params }),
  toggleUserAdmin: (userId) => api.put(`/admin/users/${userId}/toggle-admin`),
  reprocessAnalysis: (analysisId) => api.post(`/admin/analyses/${analysisId}/reprocess`),
  getSystemStats: () => api.get('/admin/stats'),
}
