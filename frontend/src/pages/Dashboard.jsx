import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Briefcase, FileText, Upload, TrendingUp, Clock, CheckCircle, ClipboardList } from 'lucide-react'
import { jobsAPI, resumesAPI, applicationsAPI } from '../services/api'
import toast from 'react-hot-toast'

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalJobs: 0,
    myResumes: 0,
    myApplications: 0,
    completedAnalyses: 0,
    pendingAnalyses: 0
  })
  const [recentJobs, setRecentJobs] = useState([])
  const [recentAnalyses, setRecentAnalyses] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      
      // Fetch jobs
      const jobsResponse = await jobsAPI.getJobs({ per_page: 5 })
      setRecentJobs(jobsResponse.data.jobs || [])
      setStats(prev => ({ ...prev, totalJobs: jobsResponse.data.total || 0 }))
      
      // Fetch user's resumes
      const resumesResponse = await resumesAPI.getResumes()
      setStats(prev => ({ ...prev, myResumes: resumesResponse.data.total || 0 }))
      
      // Fetch applications
      const applicationsResponse = await applicationsAPI.getApplications({ per_page: 5 })
      setStats(prev => ({ ...prev, myApplications: applicationsResponse.data.total || 0 }))
      
      // Fetch analyses
      const analysesResponse = await resumesAPI.getAnalyses({ per_page: 5 })
      setRecentAnalyses(analysesResponse.data.analyses || [])
      
      const completedCount = (analysesResponse.data.analyses || []).filter(a => a.analysis_status === 'completed').length
      const pendingCount = (analysesResponse.data.analyses || []).filter(a => a.analysis_status === 'pending').length
      
      setStats(prev => ({
        ...prev,
        completedAnalyses: completedCount,
        pendingAnalyses: pendingCount
      }))
      
    } catch (error) {
      toast.error('Failed to fetch dashboard data')
      console.error('Dashboard error:', error)
    } finally {
      setLoading(false)
    }
  }

  const getVerdictColor = (verdict) => {
    switch (verdict) {
      case 'High': return 'text-green-600 bg-green-100'
      case 'Medium': return 'text-yellow-600 bg-yellow-100'
      case 'Low': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100'
      case 'pending': return 'text-yellow-600 bg-yellow-100'
      case 'processing': return 'text-blue-600 bg-blue-100'
      case 'failed': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Welcome to your Resume Analyzer dashboard</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Briefcase className="h-8 w-8 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Available Jobs</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.totalJobs}</p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <FileText className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">My Resumes</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.myResumes}</p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ClipboardList className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">My Applications</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.myApplications}</p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Completed Analyses</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.completedAnalyses}</p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Clock className="h-8 w-8 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Pending Analyses</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.pendingAnalyses}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            to="/jobs"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Briefcase className="h-6 w-6 text-primary-600 mr-3" />
            <div>
              <p className="font-medium text-gray-900">Browse Jobs</p>
              <p className="text-sm text-gray-500">View available positions</p>
            </div>
          </Link>

          <Link
            to="/upload-resume"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Upload className="h-6 w-6 text-green-600 mr-3" />
            <div>
              <p className="font-medium text-gray-900">Upload Resume</p>
              <p className="text-sm text-gray-500">Add a new resume</p>
            </div>
          </Link>

          <Link
            to="/my-resumes"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <FileText className="h-6 w-6 text-blue-600 mr-3" />
            <div>
              <p className="font-medium text-gray-900">My Resumes</p>
              <p className="text-sm text-gray-500">Manage your resumes</p>
            </div>
          </Link>
        </div>
      </div>

      {/* Recent Jobs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Jobs</h2>
          <div className="space-y-4">
            {recentJobs.map((job) => (
              <div key={job.id} className="border-l-4 border-primary-500 pl-4">
                <h3 className="font-medium text-gray-900">{job.title}</h3>
                <p className="text-sm text-gray-600">{job.company}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {new Date(job.created_at).toLocaleDateString()}
                </p>
              </div>
            ))}
            {recentJobs.length === 0 && (
              <p className="text-gray-500">No recent jobs available</p>
            )}
          </div>
          <div className="mt-4">
            <Link
              to="/jobs"
              className="text-primary-600 hover:text-primary-500 text-sm font-medium"
            >
              View all jobs →
            </Link>
          </div>
        </div>

        {/* Recent Analyses */}
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Analyses</h2>
          <div className="space-y-4">
            {recentAnalyses.map((analysis) => (
              <div key={analysis.id} className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">
                    {analysis.resume?.original_filename || 'Resume'}
                  </p>
                  <p className="text-sm text-gray-600">
                    Score: {analysis.relevance_score?.toFixed(1) || 'N/A'}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  {analysis.verdict && (
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getVerdictColor(analysis.verdict)}`}>
                      {analysis.verdict}
                    </span>
                  )}
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(analysis.analysis_status)}`}>
                    {analysis.analysis_status}
                  </span>
                </div>
              </div>
            ))}
            {recentAnalyses.length === 0 && (
              <p className="text-gray-500">No analyses yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
