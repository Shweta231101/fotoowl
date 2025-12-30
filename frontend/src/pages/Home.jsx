import { useState } from 'react'
import ImportForm from '../components/ImportForm'
import JobStatus from '../components/JobStatus'

function Home() {
  const [activeJobs, setActiveJobs] = useState([])

  const handleImportStarted = (jobId, source) => {
    setActiveJobs((prev) => [...prev, { id: jobId, source }])
  }

  const handleJobComplete = (jobId) => {
    setActiveJobs((prev) => prev.filter((job) => job.id !== jobId))
  }

  return (
    <div className="space-y-8">
      {/* Import Forms */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Google Drive Import */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Import from Google Drive
          </h2>
          <ImportForm
            source="google-drive"
            placeholder="https://drive.google.com/drive/folders/..."
            onImportStarted={handleImportStarted}
          />
        </div>

        {/* Dropbox Import */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Import from Dropbox
          </h2>
          <ImportForm
            source="dropbox"
            placeholder="https://www.dropbox.com/sh/..."
            onImportStarted={handleImportStarted}
          />
        </div>
      </div>

      {/* Active Jobs */}
      {activeJobs.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Active Import Jobs
          </h2>
          <div className="space-y-4">
            {activeJobs.map((job) => (
              <JobStatus
                key={job.id}
                jobId={job.id}
                source={job.source}
                onComplete={() => handleJobComplete(job.id)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-2">
          How to use
        </h3>
        <ol className="list-decimal list-inside space-y-2 text-blue-800">
          <li>
            Make sure your Google Drive or Dropbox folder is <strong>public</strong>
          </li>
          <li>Copy the folder URL from your browser</li>
          <li>Paste the URL in the appropriate form above</li>
          <li>Click "Import" to start the import process</li>
          <li>
            View your imported images in the{' '}
            <a href="/images" className="underline">
              Images
            </a>{' '}
            page
          </li>
        </ol>
      </div>
    </div>
  )
}

export default Home
