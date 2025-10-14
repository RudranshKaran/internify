'use client'

import { useState, useRef } from 'react'
import { Upload, FileText, CheckCircle, X } from 'lucide-react'

interface ResumeUploaderProps {
  onUpload: (file: File) => void
  onRemove?: () => void
  isUploading?: boolean
  uploadedFileName?: string
}

export default function ResumeUploader({
  onUpload,
  onRemove,
  isUploading = false,
  uploadedFileName,
}: ResumeUploaderProps) {
  const [dragActive, setDragActive] = useState(false)
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

  if (uploadedFileName) {
    return (
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
          {onRemove && (
            <button
              onClick={onRemove}
              className="p-2 hover:bg-red-50 rounded-full transition-colors"
            >
              <X className="w-5 h-5 text-red-600" />
            </button>
          )}
        </div>
      </div>
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
