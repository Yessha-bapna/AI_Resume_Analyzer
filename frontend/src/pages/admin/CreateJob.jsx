import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Briefcase, ArrowLeft, FileText, Upload } from 'lucide-react'
import { jobsAPI } from '../../services/api'
import toast from 'react-hot-toast'

export default function CreateJob() {
  const [formData, setFormData] = useState({
    title: '',
    company: '',
    description: '',
    requirements: '',
    location: '',
    experience_level: '',
    employment_type: ''
  })
  const [jdPdf, setJdPdf] = useState(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      if (file.type !== 'application/pdf') {
        toast.error('Please select a PDF file')
        return
      }
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        toast.error('File size must be less than 10MB')
        return
      }
      setJdPdf(file)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      // Create FormData for multipart upload
      const submitData = new FormData()
      
      // Add form fields
      Object.keys(formData).forEach(key => {
        submitData.append(key, formData[key])
      })
      
      // Add PDF file if selected
      if (jdPdf) {
        submitData.append('jd_pdf', jdPdf)
      }

      await jobsAPI.createJob(submitData)
      toast.success('Job posting created successfully!')
      navigate('/admin')
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to create job posting')
    } finally {
      setLoading(false)
    }
  }

  const employmentTypes = [
    'Full-time',
    'Part-time',
    'Contract',
    'Internship',
    'Freelance',
    'Remote'
  ]

  const experienceLevels = [
    'Entry Level',
    'Mid Level',
    'Senior Level',
    'Executive',
    'Intern'
  ]

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/admin')}
          className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Job Posting</h1>
          <p className="text-gray-600">Add a new job description for resume analysis</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                Job Title *
              </label>
              <input
                type="text"
                id="title"
                name="title"
                required
                className="input"
                placeholder="e.g., Software Engineer"
                value={formData.title}
                onChange={handleChange}
              />
            </div>

            <div>
              <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-2">
                Company
              </label>
              <input
                type="text"
                id="company"
                name="company"
                className="input"
                placeholder="e.g., Tech Corp"
                value={formData.company}
                onChange={handleChange}
              />
            </div>

            <div>
              <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
                Location
              </label>
              <input
                type="text"
                id="location"
                name="location"
                className="input"
                placeholder="e.g., San Francisco, CA"
                value={formData.location}
                onChange={handleChange}
              />
            </div>

            <div>
              <label htmlFor="employment_type" className="block text-sm font-medium text-gray-700 mb-2">
                Employment Type
              </label>
              <select
                id="employment_type"
                name="employment_type"
                className="input"
                value={formData.employment_type}
                onChange={handleChange}
              >
                <option value="">Select employment type</option>
                {employmentTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="experience_level" className="block text-sm font-medium text-gray-700 mb-2">
                Experience Level
              </label>
              <select
                id="experience_level"
                name="experience_level"
                className="input"
                value={formData.experience_level}
                onChange={handleChange}
              >
                <option value="">Select experience level</option>
                {experienceLevels.map(level => (
                  <option key={level} value={level}>{level}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Job Details</h2>
          
          <div className="space-y-6">
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                Job Description *
              </label>
              <textarea
                id="description"
                name="description"
                required
                rows={6}
                className="input"
                placeholder="Provide a detailed description of the role, responsibilities, and what the candidate will be working on..."
                value={formData.description}
                onChange={handleChange}
              />
              <p className="mt-1 text-sm text-gray-500">
                Be specific about technologies, frameworks, and methodologies used
              </p>
            </div>

            <div>
              <label htmlFor="requirements" className="block text-sm font-medium text-gray-700 mb-2">
                Requirements
              </label>
              <textarea
                id="requirements"
                name="requirements"
                rows={4}
                className="input"
                placeholder="List the required skills, qualifications, and experience..."
                value={formData.requirements}
                onChange={handleChange}
              />
              <p className="mt-1 text-sm text-gray-500">
                Include technical skills, soft skills, education requirements, and years of experience
              </p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Job Description PDF (Optional)</h2>
          
          <div className="space-y-4">
            <div>
              <label htmlFor="jd_pdf" className="block text-sm font-medium text-gray-700 mb-2">
                Upload Job Description PDF
              </label>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md hover:border-gray-400 transition-colors">
                <div className="space-y-1 text-center">
                  {jdPdf ? (
                    <div className="flex items-center justify-center space-x-2 text-green-600">
                      <FileText className="h-8 w-8" />
                      <div>
                        <p className="text-sm font-medium">{jdPdf.name}</p>
                        <p className="text-xs text-gray-500">
                          {(jdPdf.size / (1024 * 1024)).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center">
                      <Upload className="h-8 w-8 text-gray-400" />
                      <div className="flex text-sm text-gray-600">
                        <label
                          htmlFor="jd_pdf"
                          className="relative cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500"
                        >
                          <span>Upload a PDF file</span>
                          <input
                            id="jd_pdf"
                            name="jd_pdf"
                            type="file"
                            accept=".pdf"
                            className="sr-only"
                            onChange={handleFileChange}
                          />
                        </label>
                        <p className="pl-1">or drag and drop</p>
                      </div>
                      <p className="text-xs text-gray-500">PDF up to 10MB</p>
                    </div>
                  )}
                </div>
              </div>
              <p className="mt-2 text-sm text-gray-500">
                Upload a PDF version of the job description. This will be used in addition to the text description for resume analysis.
              </p>
              {jdPdf && (
                <button
                  type="button"
                  onClick={() => setJdPdf(null)}
                  className="mt-2 text-sm text-red-600 hover:text-red-800"
                >
                  Remove file
                </button>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center justify-end space-x-4">
          <button
            type="button"
            onClick={() => navigate('/admin')}
            className="btn btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Creating...
              </div>
            ) : (
              'Create Job Posting'
            )}
          </button>
        </div>
      </form>

      {/* Tips */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Tips for Better Analysis</h3>
        <div className="space-y-3 text-sm text-gray-600">
          <div className="flex items-start">
            <Briefcase className="h-4 w-4 text-primary-600 mt-1 mr-3 flex-shrink-0" />
            <div>
              <p className="font-medium">Be Specific with Technical Skills</p>
              <p>Mention specific programming languages, frameworks, and tools to improve matching accuracy</p>
            </div>
          </div>
          <div className="flex items-start">
            <Briefcase className="h-4 w-4 text-primary-600 mt-1 mr-3 flex-shrink-0" />
            <div>
              <p className="font-medium">Include Experience Levels</p>
              <p>Specify years of experience required for different skill areas</p>
            </div>
          </div>
          <div className="flex items-start">
            <Briefcase className="h-4 w-4 text-primary-600 mt-1 mr-3 flex-shrink-0" />
            <div>
              <p className="font-medium">Separate Must-Have vs Nice-to-Have</p>
              <p>Clearly distinguish between required and preferred qualifications</p>
            </div>
          </div>
          <div className="flex items-start">
            <FileText className="h-4 w-4 text-primary-600 mt-1 mr-3 flex-shrink-0" />
            <div>
              <p className="font-medium">Upload PDF Job Description</p>
              <p>Include a PDF version for more comprehensive resume analysis and better matching accuracy</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
