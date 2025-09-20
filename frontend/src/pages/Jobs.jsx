import { useState, useEffect } from 'react'
import { Search, MapPin, Calendar, Briefcase, Building } from 'lucide-react'
import { jobsAPI } from '../services/api'
import ApplyJobModal from '../components/ApplyJobModal'
import toast from 'react-hot-toast'

export default function Jobs() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [selectedJob, setSelectedJob] = useState(null)
  const [showApplyModal, setShowApplyModal] = useState(false)

  useEffect(() => {
    fetchJobs()
  }, [currentPage, searchTerm])

  const fetchJobs = async () => {
    try {
      setLoading(true)
      const response = await jobsAPI.getJobs({
        page: currentPage,
        per_page: 12,
        search: searchTerm || undefined
      })
      
      setJobs(response.data.jobs)
      setTotalPages(response.data.pages)
    } catch (error) {
      toast.error('Failed to fetch jobs')
      console.error('Jobs fetch error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e) => {
    e.preventDefault()
    setCurrentPage(1)
    fetchJobs()
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const truncateText = (text, maxLength) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }

  const handleApplyNow = (job) => {
    setSelectedJob(job)
    setShowApplyModal(true)
  }

  const handleCloseModal = () => {
    setShowApplyModal(false)
    setSelectedJob(null)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Available Jobs</h1>
        <p className="text-gray-600">Browse and apply to job positions</p>
      </div>

      {/* Search */}
      <div className="card p-6">
        <form onSubmit={handleSearch} className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search jobs by title, company, or description..."
              className="input pl-10"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn-primary">
            Search
          </button>
        </form>
      </div>

      {/* Jobs Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <>
          {jobs.length === 0 ? (
            <div className="card p-12 text-center">
              <Briefcase className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-4 text-lg font-medium text-gray-900">No jobs found</h3>
              <p className="mt-2 text-gray-500">
                {searchTerm ? 'Try adjusting your search terms' : 'No jobs are currently available'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {jobs.map((job) => (
                <div key={job.id} className="card p-6 hover:shadow-lg transition-shadow">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {job.title}
                      </h3>
                      <div className="flex items-center text-sm text-gray-600 mb-2">
                        <Building className="h-4 w-4 mr-1" />
                        {job.company || 'Company not specified'}
                      </div>
                      {job.location && (
                        <div className="flex items-center text-sm text-gray-600 mb-2">
                          <MapPin className="h-4 w-4 mr-1" />
                          {job.location}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="mb-4">
                    <p className="text-sm text-gray-700 line-clamp-3">
                      {truncateText(job.description, 150)}
                    </p>
                  </div>

                  {job.requirements && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Requirements:</h4>
                      <p className="text-sm text-gray-600 line-clamp-2">
                        {truncateText(job.requirements, 100)}
                      </p>
                    </div>
                  )}

                  <div className="flex items-center justify-between">
                    <div className="flex items-center text-sm text-gray-500">
                      <Calendar className="h-4 w-4 mr-1" />
                      Posted {formatDate(job.created_at)}
                    </div>
                    <div className="flex items-center space-x-2">
                      {job.employment_type && (
                        <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                          {job.employment_type}
                        </span>
                      )}
                      {job.experience_level && (
                        <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                          {job.experience_level}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">
                        {job.application_count} application{job.application_count !== 1 ? 's' : ''}
                      </span>
                      <button 
                        onClick={() => handleApplyNow(job)}
                        className="text-primary-600 hover:text-primary-500 font-medium"
                      >
                        Apply Now
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

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
        </>
      )}

      {/* Apply Job Modal */}
      {selectedJob && (
        <ApplyJobModal
          isOpen={showApplyModal}
          onClose={handleCloseModal}
          job={selectedJob}
        />
      )}
    </div>
  )
}
