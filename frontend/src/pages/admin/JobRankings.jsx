import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { 
  ArrowLeft, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  RefreshCw,
  User,
  FileText,
  Star
} from 'lucide-react'
import { adminAPI } from '../../services/api'
import toast from 'react-hot-toast'

export default function JobRankings() {
  const { jobId } = useParams()
  const navigate = useNavigate()
  const [job, setJob] = useState(null)
  const [rankings, setRankings] = useState([])
  const [queueStatus, setQueueStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    if (jobId) {
      fetchJobRankings()
    }
  }, [jobId])

  const fetchJobRankings = async () => {
    try {
      setLoading(true)
      
      const [rankingsResponse, queueResponse] = await Promise.all([
        adminAPI.getJobRankings(jobId),
        adminAPI.getQueueStatus(jobId)
      ])
      
      setJob(rankingsResponse.data.job)
      setRankings(rankingsResponse.data.rankings)
      setQueueStatus(queueResponse.data.queue_status)
      
    } catch (error) {
      toast.error('Failed to fetch job rankings')
      console.error('Job rankings error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await fetchJobRankings()
    setRefreshing(false)
    toast.success('Rankings updated')
  }

  const getVerdictColor = (verdict) => {
    switch (verdict) {
      case 'High': return 'text-green-600 bg-green-100 border-green-200'
      case 'Medium': return 'text-yellow-600 bg-yellow-100 border-yellow-200'
      case 'Low': return 'text-red-600 bg-red-100 border-red-200'
      default: return 'text-gray-600 bg-gray-100 border-gray-200'
    }
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!job) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-4 text-lg font-medium text-gray-900">Job not found</h3>
        <p className="mt-2 text-gray-500">The requested job posting could not be found.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/admin')}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Job Rankings</h1>
            <p className="text-gray-600">{job.title} - {job.company}</p>
          </div>
        </div>
        
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="btn btn-secondary disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Job Info */}
      <div className="card p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">{job.title}</h2>
            <p className="text-gray-600 mb-4">{job.company}</p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              {job.location && (
                <div>
                  <span className="font-medium text-gray-700">Location:</span>
                  <span className="ml-2 text-gray-600">{job.location}</span>
                </div>
              )}
              {job.employment_type && (
                <div>
                  <span className="font-medium text-gray-700">Type:</span>
                  <span className="ml-2 text-gray-600">{job.employment_type}</span>
                </div>
              )}
              {job.experience_level && (
                <div>
                  <span className="font-medium text-gray-700">Level:</span>
                  <span className="ml-2 text-gray-600">{job.experience_level}</span>
                </div>
              )}
            </div>
          </div>
          
          <div className="text-right">
            <p className="text-sm text-gray-500">Posted</p>
            <p className="font-medium">{formatDate(job.created_at)}</p>
          </div>
        </div>
      </div>

      {/* Queue Status */}
      {queueStatus && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Queue Status</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <Clock className="h-6 w-6 text-blue-600 mx-auto mb-2" />
              <p className="text-2xl font-semibold text-blue-900">{queueStatus.pending}</p>
              <p className="text-sm text-blue-600">Pending</p>
            </div>
            
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <RefreshCw className="h-6 w-6 text-yellow-600 mx-auto mb-2" />
              <p className="text-2xl font-semibold text-yellow-900">{queueStatus.processing}</p>
              <p className="text-sm text-yellow-600">Processing</p>
            </div>
            
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <CheckCircle className="h-6 w-6 text-green-600 mx-auto mb-2" />
              <p className="text-2xl font-semibold text-green-900">{queueStatus.completed}</p>
              <p className="text-sm text-green-600">Completed</p>
            </div>
            
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <TrendingUp className="h-6 w-6 text-gray-600 mx-auto mb-2" />
              <p className="text-2xl font-semibold text-gray-900">{queueStatus.total_in_queue}</p>
              <p className="text-sm text-gray-600">Total in Queue</p>
            </div>
          </div>
          
          {queueStatus.estimated_wait_time > 0 && (
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                Estimated wait time: {queueStatus.estimated_wait_time} minutes
              </p>
            </div>
          )}
        </div>
      )}

      {/* Rankings */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Resume Rankings</h3>
          <p className="text-sm text-gray-500">
            {rankings.length} candidate{rankings.length !== 1 ? 's' : ''} analyzed
          </p>
        </div>

        {rankings.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-4 text-lg font-medium text-gray-900">No analyses yet</h3>
            <p className="mt-2 text-gray-500">
              Resumes will appear here once they are analyzed for this job posting.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {rankings.map((analysis, index) => (
              <div
                key={analysis.id}
                className={`border rounded-lg p-4 transition-all ${
                  index === 0 ? 'border-primary-300 bg-primary-50' : 'border-gray-200 bg-white'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      {index === 0 && (
                        <Star className="h-5 w-5 text-yellow-500" />
                      )}
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        index === 0 ? 'bg-primary-100 text-primary-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        Rank #{analysis.rank || index + 1}
                      </span>
                      <h4 className="font-semibold text-gray-900">
                        {analysis.resume?.original_filename || 'Resume'}
                      </h4>
                    </div>
                    
                    <div className="flex items-center space-x-4 text-sm text-gray-600 mb-3">
                      <div className="flex items-center">
                        <User className="h-4 w-4 mr-1" />
                        {analysis.user?.username || 'Unknown User'}
                      </div>
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        {formatDate(analysis.created_at)}
                      </div>
                    </div>

                    {/* Score and Verdict */}
                    <div className="flex items-center space-x-4 mb-3">
                      <div className="flex items-center">
                        <span className="text-sm font-medium text-gray-700 mr-2">Score:</span>
                        <span className={`text-lg font-bold ${getScoreColor(analysis.relevance_score)}`}>
                          {analysis.relevance_score?.toFixed(1) || 'N/A'}
                        </span>
                        <span className="text-sm text-gray-500 ml-1">/100</span>
                      </div>
                      
                      {analysis.verdict && (
                        <span className={`px-3 py-1 text-sm font-medium rounded-full border ${getVerdictColor(analysis.verdict)}`}>
                          {analysis.verdict} Suitability
                        </span>
                      )}
                    </div>

                    {/* Missing Skills */}
                    {analysis.missing_skills && analysis.missing_skills.length > 0 && (
                      <div className="mb-3">
                        <p className="text-sm font-medium text-gray-700 mb-1">Missing Skills:</p>
                        <div className="flex flex-wrap gap-1">
                          {analysis.missing_skills.slice(0, 5).map((skill, skillIndex) => (
                            <span
                              key={skillIndex}
                              className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded-full"
                            >
                              {skill}
                            </span>
                          ))}
                          {analysis.missing_skills.length > 5 && (
                            <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
                              +{analysis.missing_skills.length - 5} more
                            </span>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Improvement Suggestions */}
                    {analysis.improvement_suggestions && (
                      <div className="text-sm text-gray-600">
                        <p className="font-medium text-gray-700 mb-1">Suggestions:</p>
                        <p className="line-clamp-2">{analysis.improvement_suggestions}</p>
                      </div>
                    )}
                  </div>

                  <div className="ml-4 text-right">
                    <div className="flex items-center space-x-2">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      <span className="text-sm text-green-600 font-medium">
                        {analysis.analysis_status}
                      </span>
                    </div>
                    {analysis.analysis_completed_at && (
                      <p className="text-xs text-gray-500 mt-1">
                        {formatDate(analysis.analysis_completed_at)}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
