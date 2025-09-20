import { useState, useEffect } from 'react'
import { X, FileText, CheckCircle } from 'lucide-react'
import { applicationsAPI, resumesAPI } from '../services/api'
import toast from 'react-hot-toast'

export default function ApplyJobModal({ isOpen, onClose, job }) {
  const [resumes, setResumes] = useState([])
  const [selectedResumeId, setSelectedResumeId] = useState('')
  const [loading, setLoading] = useState(false)
  const [applying, setApplying] = useState(false)

  useEffect(() => {
    if (isOpen) {
      fetchResumes()
    }
  }, [isOpen])

  const fetchResumes = async () => {
    try {
      setLoading(true)
      const response = await resumesAPI.getResumes()
      setResumes(response.data.resumes || [])
    } catch (error) {
      toast.error('Failed to fetch resumes')
    } finally {
      setLoading(false)
    }
  }

  const handleApply = async () => {
    if (!selectedResumeId) {
      toast.error('Please select a resume')
      return
    }

    try {
      setApplying(true)
      await applicationsAPI.applyForJob({
        job_id: job.id,
        resume_id: parseInt(selectedResumeId)
      })
      
      toast.success('Application submitted successfully!')
      onClose()
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to apply for job')
    } finally {
      setApplying(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Apply for Job</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-2">{job.title}</h3>
            <p className="text-sm text-gray-600">{job.company}</p>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Resume
            </label>
            
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
              </div>
            ) : resumes.length === 0 ? (
              <div className="text-center py-8">
                <FileText className="mx-auto h-12 w-12 text-gray-400" />
                <p className="mt-2 text-sm text-gray-500">No resumes found</p>
                <p className="text-xs text-gray-400">Upload a resume first to apply for jobs</p>
              </div>
            ) : (
              <div className="space-y-3">
                {resumes.map((resume) => (
                  <label
                    key={resume.id}
                    className={`flex items-center p-3 border rounded-lg cursor-pointer transition-colors ${
                      selectedResumeId === resume.id.toString()
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name="resume"
                      value={resume.id}
                      checked={selectedResumeId === resume.id.toString()}
                      onChange={(e) => setSelectedResumeId(e.target.value)}
                      className="sr-only"
                    />
                    <div className="flex items-center space-x-3">
                      <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                        selectedResumeId === resume.id.toString()
                          ? 'border-primary-500 bg-primary-500'
                          : 'border-gray-300'
                      }`}>
                        {selectedResumeId === resume.id.toString() && (
                          <CheckCircle className="h-3 w-3 text-white" />
                        )}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">
                          {resume.original_filename}
                        </p>
                        <p className="text-xs text-gray-500">
                          Uploaded {new Date(resume.uploaded_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            )}
          </div>

          <div className="flex items-center justify-end space-x-3">
            <button
              onClick={onClose}
              className="btn btn-secondary"
              disabled={applying}
            >
              Cancel
            </button>
            <button
              onClick={handleApply}
              disabled={applying || !selectedResumeId || resumes.length === 0}
              className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {applying ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Applying...
                </div>
              ) : (
                'Apply Now'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
