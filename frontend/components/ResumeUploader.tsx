'use client'

import { useState, useRef } from 'react'
import { Upload, FileText, CheckCircle, X, RefreshCw, Trash2 } from 'lucide-react'

interface ResumeUploaderProps {
  onUpload: (file: File) => void
  onRemove?: () => void
  onDelete?: () => void
  isUploading?: boolean
  uploadedFileName?: string
}

export default function ResumeUploader({
  onUpload,
  onRemove,
  onDelete,
  isUploading = false,
  uploadedFileName,
}: ResumeUploaderProps) {
  const [dragActive, setDragActive] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = (file: File) => {
    if (file.type === 'application/pdf') {
      onUpload(file)
    } else {
      alert('Please upload a PDF file')
    }
  }

  const handleClick = () => {
    inputRef.current?.click()
  }

  const handleDeleteClick = () => {
    setShowDeleteConfirm(true)
  }

  const handleDeleteConfirm = () => {
    setShowDeleteConfirm(false)
    if (onDelete) {
      onDelete()
    }
  }

  const handleDeleteCancel = () => {
    setShowDeleteConfirm(false)
  }

  if (uploadedFileName) {
    return (
      <>
        <div className="border-2 border-green-200 bg-green-50 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Resume Uploaded</p>
                <p className="text-xs text-gray-600">{uploadedFileName}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {/* Replace Resume Button */}
              <button
                onClick={handleClick}
                className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
                title="Replace with a new resume"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Replace</span>
              </button>
              {/* Delete Resume Button */}
              {onDelete && (
                <button
                  onClick={handleDeleteClick}
                  className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
                  title="Delete resume"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>Delete</span>
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Delete Confirmation Modal */}
        {showDeleteConfirm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md mx-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Delete Resume?</h3>
              <p className="text-gray-600 mb-6">
                Are you sure you want to delete your resume? This action cannot be undone.
              </p>
              <div className="flex justify-end gap-3">
                <button
                  onClick={handleDeleteCancel}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteConfirm}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        )}
      </>
    )
  }

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
        dragActive
          ? 'border-primary bg-primary/5'
          : 'border-gray-300 hover:border-primary hover:bg-gray-50'
      } ${isUploading ? 'opacity-50 pointer-events-none' : ''}`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        onChange={handleChange}
        className="hidden"
      />

      <div className="space-y-4">
        <div className="flex justify-center">
          <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
            {isUploading ? (
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            ) : (
              <Upload className="w-8 h-8 text-primary" />
            )}
          </div>
        </div>

        <div>
          <p className="text-lg font-medium text-gray-900 mb-1">
            {isUploading ? 'Uploading...' : 'Upload your resume'}
          </p>
          <p className="text-sm text-gray-600">
            Drag and drop your PDF file here, or click to browse
          </p>
        </div>

        <div className="flex items-center justify-center space-x-2 text-xs text-gray-500">
          <FileText className="w-4 h-4" />
          <span>PDF format only • Max 10MB</span>
        </div>
      </div>
    </div>
  )
}
