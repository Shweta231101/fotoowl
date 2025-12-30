import { useState } from 'react'
import api from '../services/api'

function ImportForm({ source, placeholder, onImportStarted }) {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!url.trim()) {
      setError('Please enter a folder URL')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const response = await api.importFromSource(source, url)
      setSuccess(`Import started! Job ID: ${response.job_id}`)
      onImportStarted(response.job_id, source)
      setUrl('')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start import')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor={`url-${source}`} className="sr-only">
          Folder URL
        </label>
        <input
          type="text"
          id={`url-${source}`}
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder={placeholder}
          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          disabled={loading}
        />
      </div>

      {error && (
        <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
          {error}
        </div>
      )}

      {success && (
        <div className="text-sm text-green-600 bg-green-50 p-2 rounded">
          {success}
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <>
            <svg
              className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            Importing...
          </>
        ) : (
          'Import'
        )}
      </button>
    </form>
  )
}

export default ImportForm
