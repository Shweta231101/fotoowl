import axios from 'axios'

// API base URL - defaults to localhost for development
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

const api = {
  /**
   * Import images from a source (Google Drive or Dropbox)
   * @param {string} source - 'google-drive' or 'dropbox'
   * @param {string} folderUrl - The public folder URL
   * @returns {Promise} - Import response with job_id
   */
  importFromSource: async (source, folderUrl) => {
    const endpoint = `/import/${source}`
    const response = await client.post(endpoint, { folder_url: folderUrl })
    return response.data
  },

  /**
   * Get job status
   * @param {string} jobId - The job ID to check
   * @returns {Promise} - Job status response
   */
  getJobStatus: async (jobId) => {
    const response = await client.get(`/import/jobs/${jobId}`)
    return response.data
  },

  /**
   * Get list of imported images
   * @param {Object} params - Query parameters
   * @param {number} params.page - Page number
   * @param {number} params.limit - Items per page
   * @param {string} params.source - Filter by source
   * @returns {Promise} - Paginated image list
   */
  getImages: async (params = {}) => {
    const response = await client.get('/images', { params })
    return response.data
  },

  /**
   * Get a single image by ID
   * @param {number} imageId - The image ID
   * @returns {Promise} - Image details
   */
  getImage: async (imageId) => {
    const response = await client.get(`/images/${imageId}`)
    return response.data
  },
}

export default api
