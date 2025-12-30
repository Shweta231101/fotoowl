import { useState, useEffect } from 'react'
import api from '../services/api'

function JobStatus({ jobId, source, onComplete }) {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let intervalId

    const fetchStatus = async () => {
      try {
        const data = await api.getJobStatus(jobId)
        setStatus(data)
        setError(null)

        // Check if job is complete
        if (
          data.status === 'completed' ||
          data.status === 'completed_with_errors' ||
          data.status === 'failed'
        ) {
          clearInterval(intervalId)
          setTimeout(() => onComplete(), 3000) // Remove after 3 seconds
        }
      } catch (err) {
        setError('Failed to fetch job status')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    // Fetch immediately
    fetchStatus()

    // Then poll every 2 seconds
    intervalId = setInterval(fetchStatus, 2000)

    return () => clearInterval(intervalId)
  }, [jobId, onComplete])

  if (loading && !status) {
    return (
      <div className="animate-pulse bg-gray-100 rounded-lg p-4">
        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-sm text-red-600">{error}</p>
      </div>
    )
  }

  const getStatusColor = () => {
    switch (status?.status) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'completed_with_errors':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'processing':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  return (
    <div className={`border rounded-lg p-4 ${getStatusColor()}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span className="font-medium">
            {source === 'google-drive' ? 'Google Drive' : 'Dropbox'} Import
          </span>
          <span className="text-xs px-2 py-0.5 rounded-full bg-white/50">
            {status?.status}
          </span>
        </div>
        <span className="text-xs opacity-75">{jobId.slice(0, 8)}...</span>
      </div>

      {/* Progress Bar */}
      {status?.total_files > 0 && (
        <div className="mt-2">
          <div className="flex justify-between text-xs mb-1">
            <span>
              {status.processed_files} / {status.total_files} files
            </span>
            <span>{status.progress_percent}%</span>
          </div>
          <div className="w-full bg-white/50 rounded-full h-2">
            <div
              className="bg-current h-2 rounded-full transition-all duration-300"
              style={{ width: `${status.progress_percent}%` }}
            ></div>
          </div>
          {status.failed_files > 0 && (
            <p className="text-xs mt-1">
              {status.failed_files} failed
            </p>
          )}
        </div>
      )}

      {status?.error_message && (
        <p className="text-xs mt-2 opacity-75">{status.error_message}</p>
      )}
    </div>
  )
}

export default JobStatus
