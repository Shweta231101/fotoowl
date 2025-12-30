import { useState, useEffect } from 'react'
import ImageList from '../components/ImageList'
import api from '../services/api'

function Images() {
  const [images, setImages] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('')
  const [pagination, setPagination] = useState({
    page: 1,
    pages: 1,
    total: 0,
    pageSize: 20,
  })

  const fetchImages = async (page = 1, source = '') => {
    setLoading(true)
    setError(null)

    try {
      const params = { page, limit: 20 }
      if (source) {
        params.source = source
      }

      const response = await api.getImages(params)
      setImages(response.images)
      setPagination({
        page: response.page,
        pages: response.pages,
        total: response.total,
        pageSize: response.page_size,
      })
    } catch (err) {
      setError('Failed to load images. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchImages(1, filter)
  }, [filter])

  const handlePageChange = (newPage) => {
    fetchImages(newPage, filter)
  }

  const handleFilterChange = (e) => {
    setFilter(e.target.value)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Imported Images</h2>
        <div className="flex items-center space-x-4">
          {/* Source Filter */}
          <select
            value={filter}
            onChange={handleFilterChange}
            className="block w-48 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          >
            <option value="">All Sources</option>
            <option value="google_drive">Google Drive</option>
            <option value="dropbox">Dropbox</option>
          </select>

          {/* Refresh Button */}
          <button
            onClick={() => fetchImages(pagination.page, filter)}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg
              className="h-4 w-4 mr-1"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            Refresh
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="bg-white shadow rounded-lg p-4">
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-600">
            Showing {images.length} of {pagination.total} images
          </p>
          {filter && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {filter === 'google_drive' ? 'Google Drive' : 'Dropbox'}
            </span>
          )}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      ) : images.length === 0 ? (
        <div className="text-center py-12">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No images</h3>
          <p className="mt-1 text-sm text-gray-500">
            Import images from Google Drive or Dropbox to get started.
          </p>
        </div>
      ) : (
        <>
          {/* Image Grid */}
          <ImageList images={images} />

          {/* Pagination */}
          {pagination.pages > 1 && (
            <div className="flex justify-center space-x-2">
              <button
                onClick={() => handlePageChange(pagination.page - 1)}
                disabled={pagination.page === 1}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <span className="px-4 py-2 text-sm text-gray-700">
                Page {pagination.page} of {pagination.pages}
              </span>
              <button
                onClick={() => handlePageChange(pagination.page + 1)}
                disabled={pagination.page === pagination.pages}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default Images
