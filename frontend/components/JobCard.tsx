'use client'

import { MapPin, Building, ExternalLink, Calendar } from 'lucide-react'
import { formatDate, truncateText } from '@/lib/utils'

interface JobCardProps {
  job: {
    id?: string
    title: string
    company: string
    location?: string
    description?: string
    link?: string
    posted_at?: string
  }
  onSelect?: (job: any) => void
  selected?: boolean
}

export default function JobCard({ job, onSelect, selected }: JobCardProps) {
  return (
    <div
      onClick={() => onSelect && onSelect(job)}
      className={`border rounded-lg p-5 hover:shadow-lg transition-all cursor-pointer ${
        selected
          ? 'border-primary bg-primary/5 shadow-md'
          : 'border-gray-200 hover:border-primary/50'
      }`}
    >
      <div className="space-y-3">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              {job.title}
            </h3>
            <div className="flex items-center space-x-2 text-gray-600">
              <Building className="w-4 h-4" />
              <span className="text-sm font-medium">{job.company}</span>
            </div>
          </div>

          {selected && (
            <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary flex items-center justify-center">
              <svg
                className="w-4 h-4 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
          )}
        </div>

        {/* Location */}
        {job.location && (
          <div className="flex items-center space-x-2 text-gray-500">
            <MapPin className="w-4 h-4" />
            <span className="text-sm">{job.location}</span>
          </div>
        )}

        {/* Description */}
        {job.description && (
          <p className="text-sm text-gray-600 line-clamp-3">
            {truncateText(job.description, 150)}
          </p>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between pt-2 border-t border-gray-100">
          {job.posted_at && (
            <div className="flex items-center space-x-1 text-xs text-gray-500">
              <Calendar className="w-3 h-3" />
              <span>{formatDate(job.posted_at)}</span>
            </div>
          )}

          {job.link && (
            <a
              href={job.link}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="flex items-center space-x-1 text-primary hover:text-primary/80 text-sm font-medium"
            >
              <span>View Posting</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          )}
        </div>
      </div>
    </div>
  )
}
