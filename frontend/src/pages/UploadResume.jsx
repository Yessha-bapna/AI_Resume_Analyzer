import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react'
import { resumesAPI } from '../services/api'
import toast from 'react-hot-toast'

export default function UploadResume() {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const navigate = useNavigate()

  const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
  const maxSize = 16 * 1024 * 1024 // 16MB

  const handleFileSelect = (selectedFile) => {
    if (!selectedFile) return

    // Validate file type
    if (!allowedTypes.includes(selectedFile.type)) {
      toast.error('Please upload a PDF or DOCX file')
      return
    }

    // Validate file size
    if (selectedFile.size > maxSize) {
      toast.error('File size must be less than 16MB')
      return
    }

    setFile(selectedFile)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const droppedFiles = e.dataTransfer.files
    if (droppedFiles && droppedFiles.length > 0) {
      handleFileSelect(droppedFiles[0])
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
  }

  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select a file first')
      return
    }

    try {
      setUploading(true)
      
      const formData = new FormData()
      formData.append('file', file)

      const response = await resumesAPI.uploadResume(formData)
      
      toast.success('Resume uploaded successfully!')
      navigate('/my-resumes')
      
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to upload resume')
      console.error('Upload error:', error)
    } finally {
      setUploading(false)
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Upload Resume</h1>
        <p className="text-gray-600">Upload your resume in PDF or DOCX format</p>
      </div>

      <div className="card p-8">
        {/* File Drop Zone */}
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive
              ? 'border-primary-500 bg-primary-50'
              : file
              ? 'border-green-500 bg-green-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          {file ? (
            <div className="space-y-4">
              <CheckCircle className="mx-auto h-12 w-12 text-green-600" />
              <div>
                <h3 className="text-lg font-medium text-gray-900">File Selected</h3>
                <p className="text-sm text-gray-600">{file.name}</p>
                <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
              </div>
              <button
                onClick={() => setFile(null)}
                className="text-sm text-red-600 hover:text-red-500"
              >
                Remove file
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <div>
                <h3 className="text-lg font-medium text-gray-900">
                  Drop your resume here, or{' '}
                  <label className="text-primary-600 hover:text-primary-500 cursor-pointer">
                    browse files
                    <input
                      type="file"
                      accept=".pdf,.docx"
                      onChange={(e) => handleFileSelect(e.target.files[0])}
                      className="hidden"
                    />
                  </label>
                </h3>
                <p className="text-sm text-gray-600">
                  Supports PDF and DOCX files up to 16MB
                </p>
              </div>
            </div>
          )}
        </div>

        {/* File Requirements */}
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-start">
            <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5 mr-3" />
            <div className="text-sm text-blue-800">
              <h4 className="font-medium mb-2">File Requirements:</h4>
              <ul className="space-y-1 list-disc list-inside">
                <li>File formats: PDF (.pdf) or Word Document (.docx)</li>
                <li>Maximum file size: 16MB</li>
                <li>Make sure your resume is well-formatted and readable</li>
                <li>Include relevant skills, experience, and education</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Upload Button */}
        <div className="mt-6 flex justify-end">
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Uploading...
              </div>
            ) : (
              'Upload Resume'
            )}
          </button>
        </div>
      </div>

      {/* Tips */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Tips for Better Results</h3>
        <div className="space-y-3 text-sm text-gray-600">
          <div className="flex items-start">
            <FileText className="h-4 w-4 text-primary-600 mt-1 mr-3 flex-shrink-0" />
            <div>
              <p className="font-medium">Include Relevant Keywords</p>
              <p>Make sure to include technical skills and technologies mentioned in job descriptions</p>
            </div>
          </div>
          <div className="flex items-start">
            <FileText className="h-4 w-4 text-primary-600 mt-1 mr-3 flex-shrink-0" />
            <div>
              <p className="font-medium">Highlight Achievements</p>
              <p>Include specific accomplishments and project details to improve your score</p>
            </div>
          </div>
          <div className="flex items-start">
            <FileText className="h-4 w-4 text-primary-600 mt-1 mr-3 flex-shrink-0" />
            <div>
              <p className="font-medium">Keep It Current</p>
              <p>Update your resume regularly with the latest skills and experience</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
