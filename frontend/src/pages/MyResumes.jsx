import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { 
  FileText, 
  Upload, 
  Trash2, 
  Eye, 
  TrendingUp, 
  Calendar,
  Download,
  AlertCircle
} from 'lucide-react'
import { resumesAPI } from '../services/api'
import toast from 'react-hot-toast'

export default function MyResumes() {
  const [resumes, setResumes] = useState([])
  const [analyses, setAnalyses] = useState([])
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  useEffect(() => {
    fetchResumes()
    fetchAnalyses()
  }, [currentPage])

  const fetchResumes = async () => {
    try {
      const response = await resumesAPI.getResumes({
        page: currentPage,
        per_page: 10
      })
      
      setResumes(response.data.resumes)
      setTotalPages(response.data.pages)
    } catch (error) {
      toast.error('Failed to fetch resumes')
      console.error('Resumes fetch error:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchAnalyses = async () => {
    try {
      const response = await resumesAPI.getAnalyses({
        per_page: 50 // Get more analyses to show for all resumes
      })
      setAnalyses(response.data.analyses)
    } catch (error) {
      console.error('Analyses fetch error:', error)
    }
  }

  const handleDeleteResume = async (resumeId, resumeName) => {
    if (!window.confirm(`Are you sure you want to delete "${resumeName}"? This action cannot be undone.`)) {
      return
    }

    try {
      await resumesAPI.deleteResume(resumeId)
      toast.success('Resume deleted successfully')
      fetchResumes()
      fetchAnalyses()
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to delete resume')
      console.error('Delete error:', error)
    }
  }

  const handleAnalyzeResume = async (resumeId, jobId) => {
    try {
      const response = await resumesAPI.analyzeResume(resumeId, jobId)
      toast.success('Analysis started successfully!')
      fetchAnalyses()
      return response.data
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to start analysis')
      console.error('Analysis error:', error)
    }
  }

  const getResumeAnalyses = (resumeId) => {
    return analyses.filter(analysis => analysis.resume_id === resumeId)
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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Resumes</h1>
          <p className="text-gray-600">Manage your uploaded resumes and view analysis results</p>
        </div>
        <Link to="/upload-resume" className="btn btn-primary">
          <Upload className="h-4 w-4 mr-2" />
          Upload New Resume
        </Link>
      </div>

      {resumes.length === 0 ? (
        <div className="card p-12 text-center">
          <FileText className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No resumes uploaded</h3>
          <p className="mt-2 text-gray-500">
            Upload your first resume to get started with the analysis
          </p>
          <div className="mt-6">
            <Link to="/upload-resume" className="btn btn-primary">
              Upload Resume
            </Link>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {resumes.map((resume) => {
            const resumeAnalyses = getResumeAnalyses(resume.id)
            const completedAnalyses = resumeAnalyses.filter(a => a.analysis_status === 'completed')
            const pendingAnalyses = resumeAnalyses.filter(a => a.analysis_status === 'pending')
            const avgScore = completedAnalyses.length > 0 
              ? (completedAnalyses.reduce((sum, a) => sum + a.relevance_score, 0) / completedAnalyses.length).toFixed(1)
              : null

            return (
              <div key={resume.id} className="card p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <FileText className="h-5 w-5 text-primary-600" />
                      <h3 className="text-lg font-semibold text-gray-900">
                        {resume.original_filename}
                      </h3>
                      <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded-full">
                        {resume.file_type}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-4 text-sm text-gray-500 mb-4">
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 mr-1" />
                        Uploaded {formatDate(resume.uploaded_at)}
                      </div>
                      {avgScore && (
                        <div className="flex items-center">
                          <TrendingUp className="h-4 w-4 mr-1" />
                          Avg Score: {avgScore}
                        </div>
                      )}
                    </div>

                    {/* Analysis Stats */}
                    <div className="flex items-center space-x-4 text-sm">
                      <div className="flex items-center">
                        <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                        {completedAnalyses.length} completed
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></div>
                        {pendingAnalyses.length} pending
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleDeleteResume(resume.id, resume.original_filename)}
                      className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                      title="Delete resume"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {/* Recent Analyses */}
                {resumeAnalyses.length > 0 && (
                  <div className="border-t border-gray-200 pt-4">
                    <h4 className="text-sm font-medium text-gray-900 mb-3">Recent Analyses</h4>
                    <div className="space-y-3">
                      {resumeAnalyses.slice(0, 3).map((analysis) => (
                        <div key={analysis.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-1">
                              <span className="text-sm font-medium text-gray-900">
                                Job #{analysis.job_id}
                              </span>
                              {analysis.relevance_score && (
                                <span className="text-sm text-gray-600">
                                  Score: {analysis.relevance_score.toFixed(1)}
                                </span>
                              )}
                            </div>
                            <div className="flex items-center space-x-2">
                              <span className="text-xs text-gray-500">
                                {formatDate(analysis.created_at)}
                              </span>
                            </div>
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
                    </div>
                    
                    {resumeAnalyses.length > 3 && (
                      <div className="mt-3 text-center">
                        <button className="text-sm text-primary-600 hover:text-primary-500">
                          View all {resumeAnalyses.length} analyses
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {/* Quick Actions */}
                <div className="border-t border-gray-200 pt-4 mt-4">
                  <div className="flex items-center space-x-3">
                    <Link
                      to={`/jobs`}
                      className="text-sm text-primary-600 hover:text-primary-500 font-medium"
                    >
                      Browse Jobs to Apply
                    </Link>
                    <span className="text-gray-300">|</span>
                    <button
                      onClick={() => {
                        // You could implement a preview functionality here
                        toast.info('Preview functionality coming soon')
                      }}
                      className="text-sm text-gray-600 hover:text-gray-500 font-medium"
                    >
                      Preview Resume
                    </button>
                  </div>
                </div>
              </div>
            )
          })}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-700">
                Page {currentPage} of {totalPages}
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="btn btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                  className="btn btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
