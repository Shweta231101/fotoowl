function ImageList({ images }) {
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {images.map((image) => (
        <div
          key={image.id}
          className="bg-white rounded-lg shadow overflow-hidden group"
        >
          {/* Image Preview */}
          <div className="aspect-square bg-gray-100 relative">
            <img
              src={image.storage_url}
              alt={image.name}
              className="w-full h-full object-cover"
              loading="lazy"
              onError={(e) => {
                e.target.onerror = null
                e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="%239CA3AF"%3E%3Cpath stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /%3E%3C/svg%3E'
              }}
            />
            {/* Source Badge */}
            <span
              className={`absolute top-2 right-2 px-2 py-1 text-xs font-medium rounded ${
                image.source === 'google_drive'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-blue-100 text-blue-800'
              }`}
            >
              {image.source === 'google_drive' ? 'Drive' : 'Dropbox'}
            </span>
          </div>

          {/* Image Info */}
          <div className="p-3">
            <h3
              className="text-sm font-medium text-gray-900 truncate"
              title={image.name}
            >
              {image.name}
            </h3>
            <div className="mt-1 flex items-center justify-between text-xs text-gray-500">
              <span>{formatFileSize(image.size)}</span>
              <span>{image.mime_type.split('/')[1].toUpperCase()}</span>
            </div>
            <p className="mt-1 text-xs text-gray-400">
              {formatDate(image.created_at)}
            </p>
          </div>

          {/* Hover Actions */}
          <div className="p-3 pt-0 opacity-0 group-hover:opacity-100 transition-opacity">
            <a
              href={image.storage_url}
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full text-center py-1.5 px-3 border border-gray-300 rounded text-xs font-medium text-gray-700 hover:bg-gray-50"
            >
              View Full Size
            </a>
          </div>
        </div>
      ))}
    </div>
  )
}

export default ImageList
