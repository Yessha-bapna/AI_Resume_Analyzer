import { useState, useEffect } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { 
  Users, 
  Briefcase, 
  FileText, 
  TrendingUp, 
  Clock, 
  CheckCircle,
  AlertCircle,
  Plus,
  BarChart3
} from 'lucide-react'
import { adminAPI } from '../../services/api'
import { useAuth } from '../../contexts/AuthContext'
import toast from 'react-hot-toast'

export default function AdminDashboard() {
  const { user } = useAuth()
  
  if (!user?.is_admin) {
    return <Navigate to="/dashboard" />
  }
  const [stats, setStats] = useState({
    users: { total: 0, admins: 0, regular_users: 0 },
    jobs: { total: 0, active: 0, inactive: 0 },
    analyses: { total: 0, completed: 0, pending: 0, processing: 0, failed: 0 },
    verdicts: { high: 0, medium: 0, low: 0 }
  })
  const [recentJobs, setRecentJobs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      
      // Fetch system stats
      const statsResponse = await adminAPI.getSystemStats()
      setStats(statsResponse.data.stats)
      
      // Fetch recent jobs
      const jobsResponse = await adminAPI.getDashboard()
      setRecentJobs(jobsResponse.data.recent_jobs)
      
    } catch (error) {
      toast.error('Failed to fetch dashboard data')
      console.error('Admin dashboard error:', error)
    } finally {
      setLoading(false)
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
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-600">Overview of the Resume Analyzer system</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Users Stats */}
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Users className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Users</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.users.total}</p>
              <p className="text-xs text-gray-500">
                {stats.users.admins} admins, {stats.users.regular_users} users
              </p>
            </div>
          </div>
        </div>

        {/* Jobs Stats */}
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Briefcase className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Job Postings</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.jobs.active}</p>
              <p className="text-xs text-gray-500">
                {stats.jobs.inactive} inactive
              </p>
            </div>
          </div>
        </div>

        {/* Analyses Stats */}
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <FileText className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Analyses</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.analyses.total}</p>
              <p className="text-xs text-gray-500">
                {stats.analyses.completed} completed
              </p>
            </div>
          </div>
        </div>

        {/* Success Rate */}
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <TrendingUp className="h-8 w-8 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">High Suitability</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.verdicts.high}</p>
              <p className="text-xs text-gray-500">
                {stats.analyses.total > 0 
                  ? ((stats.verdicts.high / stats.analyses.total) * 100).toFixed(1) 
                  : 0}% success rate
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Analysis Status */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Status</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-green-600 mr-3" />
                <span className="text-sm font-medium text-gray-700">Completed</span>
              </div>
              <span className="text-sm font-semibold text-gray-900">{stats.analyses.completed}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Clock className="h-5 w-5 text-yellow-600 mr-3" />
                <span className="text-sm font-medium text-gray-700">Pending</span>
              </div>
              <span className="text-sm font-semibold text-gray-900">{stats.analyses.pending}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <BarChart3 className="h-5 w-5 text-blue-600 mr-3" />
                <span className="text-sm font-medium text-gray-700">Processing</span>
              </div>
              <span className="text-sm font-semibold text-gray-900">{stats.analyses.processing}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <AlertCircle className="h-5 w-5 text-red-600 mr-3" />
                <span className="text-sm font-medium text-gray-700">Failed</span>
              </div>
              <span className="text-sm font-semibold text-gray-900">{stats.analyses.failed}</span>
            </div>
          </div>
        </div>

        {/* Verdict Distribution */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Verdict Distribution</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                <span className="text-sm font-medium text-gray-700">High Suitability</span>
              </div>
              <span className="text-sm font-semibold text-gray-900">{stats.verdicts.high}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-yellow-500 rounded-full mr-3"></div>
                <span className="text-sm font-medium text-gray-700">Medium Suitability</span>
              </div>
              <span className="text-sm font-semibold text-gray-900">{stats.verdicts.medium}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-red-500 rounded-full mr-3"></div>
                <span className="text-sm font-medium text-gray-700">Low Suitability</span>
              </div>
              <span className="text-sm font-semibold text-gray-900">{stats.verdicts.low}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            to="/admin/create-job"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Plus className="h-6 w-6 text-primary-600 mr-3" />
            <div>
              <p className="font-medium text-gray-900">Create Job Posting</p>
              <p className="text-sm text-gray-500">Add a new job description</p>
            </div>
          </Link>

          <Link
            to="/admin/users"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Users className="h-6 w-6 text-blue-600 mr-3" />
            <div>
              <p className="font-medium text-gray-900">Manage Users</p>
              <p className="text-sm text-gray-500">View and manage user accounts</p>
            </div>
          </Link>

          <Link
            to="/admin/analyses"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <BarChart3 className="h-6 w-6 text-green-600 mr-3" />
            <div>
              <p className="font-medium text-gray-900">View All Analyses</p>
              <p className="text-sm text-gray-500">Monitor system performance</p>
            </div>
          </Link>
        </div>
      </div>

      {/* Recent Jobs */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Job Postings</h3>
        <div className="space-y-4">
          {recentJobs.map((job) => (
            <div key={job.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">{job.title}</h4>
                <p className="text-sm text-gray-600">{job.company}</p>
                <p className="text-xs text-gray-500">
                  Posted {new Date(job.created_at).toLocaleDateString()}
                </p>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600">
                  {job.application_count} applications
                </span>
                <Link
                  to={`/admin/jobs/${job.id}/rankings`}
                  className="text-primary-600 hover:text-primary-500 text-sm font-medium"
                >
                  View Rankings
                </Link>
              </div>
            </div>
          ))}
          {recentJobs.length === 0 && (
            <p className="text-gray-500 text-center py-4">No recent jobs</p>
          )}
        </div>
      </div>
    </div>
  )
}
