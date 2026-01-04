'use client'

import { useState } from 'react'
import { Copy, Check, Edit2 } from 'lucide-react'

interface EmailPreviewProps {
  subject: string
  body: string
  onSubjectChange?: (subject: string) => void
  onBodyChange?: (body: string) => void
  recipientEmail?: string
}

export default function EmailPreview({
  subject,
  body,
  onSubjectChange,
  onBodyChange,
  recipientEmail,
}: EmailPreviewProps) {
  const [copied, setCopied] = useState(false)
  const [isEditingSubject, setIsEditingSubject] = useState(false)
  const [isEditingBody, setIsEditingBody] = useState(false)

  const handleCopy = () => {
    const fullEmail = `Subject: ${subject}\n\n${body}`
    navigator.clipboard.writeText(fullEmail)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Email Preview</h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleCopy}
              className="flex items-center space-x-1 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4 text-green-600" />
                  <span>Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  <span>Copy</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Email Content */}
      <div className="px-6 py-4 space-y-4">
        {/* Recipient */}
        {recipientEmail && (
          <div className="flex items-start space-x-3">
            <span className="text-sm font-medium text-gray-600 w-16">To:</span>
            <span className="text-sm text-gray-900">{recipientEmail}</span>
          </div>
        )}

        {/* Subject */}
        <div className="flex items-start space-x-3">
          <span className="text-sm font-medium text-gray-600 w-16">Subject:</span>
          <div className="flex-1">
            {isEditingSubject && onSubjectChange ? (
              <input
                type="text"
                value={subject}
                onChange={(e) => onSubjectChange(e.target.value)}
                onBlur={() => setIsEditingSubject(false)}
                className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                autoFocus
              />
            ) : (
              <div className="flex items-center justify-between group">
                <p className="text-sm text-gray-900 font-medium">{subject}</p>
                {onSubjectChange && (
                  <button
                    onClick={() => setIsEditingSubject(true)}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-100 rounded transition-opacity"
                  >
                    <Edit2 className="w-3 h-3 text-gray-600" />
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Body */}
        <div className="flex items-start space-x-3">
          <span className="text-sm font-medium text-gray-600 w-16">Body:</span>
          <div className="flex-1">
            {isEditingBody && onBodyChange ? (
              <textarea
                value={body}
                onChange={(e) => onBodyChange(e.target.value)}
                onBlur={() => setIsEditingBody(false)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary min-h-[200px]"
                autoFocus
              />
            ) : (
              <div className="group">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1"></div>
                  {onBodyChange && (
                    <button
                      onClick={() => setIsEditingBody(true)}
                      className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-100 rounded transition-opacity"
                    >
                      <Edit2 className="w-3 h-3 text-gray-600" />
                    </button>
                  )}
                </div>
                <div className="prose prose-sm max-w-none">
                  <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                    {body}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 px-6 py-4 bg-gray-50 rounded-b-lg">
        <div className="flex items-center justify-between">
          <p className="text-xs text-gray-600">
            Review and edit the email, then copy it to use in your email client
          </p>
          <button
            onClick={handleCopy}
            className="flex items-center space-x-2 px-6 py-2.5 bg-primary text-white rounded-md hover:bg-primary/90 transition-colors font-medium"
          >
            {copied ? (
              <>
                <Check className="w-5 h-5" />
                <span>Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-5 h-5" />
                <span>Copy Email</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
