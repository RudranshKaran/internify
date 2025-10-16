'use client'

import { MapPin, Building, ExternalLink, Calendar } from 'lucide-react'
import { formatDate, truncateText } from '@/lib/utils'

interface InternshipCardProps {
  internship: {
    id?: string
    title: string
    company: string
    location?: string
    description?: string
    link?: string
    posted_at?: string
  }
  onSelect?: (internship: any) => void
  selected?: boolean
}

export default function InternshipCard({ internship, onSelect, selected }: InternshipCardProps) {
  return (
    <div
      onClick={() => onSelect && onSelect(internship)}
      className={`relative border-2 rounded-lg p-5 transition-all duration-200 cursor-pointer ${
        selected
          ? 'border-primary bg-primary/5 shadow-lg ring-2 ring-primary/20'
          : 'border-gray-200 hover:border-primary hover:shadow-md hover:scale-[1.02]'
      }`}
    >
      {/* "Click to select" badge for unselected cards */}
      {!selected && onSelect && (
        <div className="absolute top-3 right-3 px-2 py-1 bg-blue-50 text-blue-600 text-xs font-medium rounded border border-blue-200">
          Click to select
        </div>
      )}
      
      <div className="space-y-3">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1 pr-24">
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              {internship.title}
            </h3>
            <div className="flex items-center space-x-2 text-gray-600">
              <Building className="w-4 h-4" />
              <span className="text-sm font-medium">{internship.company}</span>
            </div>
          </div>

          {selected && (
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center shadow-md absolute top-3 right-3">
              <svg
                className="w-5 h-5 text-white"
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
        {internship.location && (
          <div className="flex items-center space-x-2 text-gray-500">
            <MapPin className="w-4 h-4" />
            <span className="text-sm">{internship.location}</span>
          </div>
        )}

        {/* Description */}
        {internship.description && (
          <p className="text-sm text-gray-600 line-clamp-3">
            {truncateText(internship.description, 150)}
          </p>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between pt-2 border-t border-gray-100">
          {internship.posted_at && (
            <div className="flex items-center space-x-1 text-xs text-gray-500">
              <Calendar className="w-3 h-3" />
              <span>{formatDate(internship.posted_at)}</span>
            </div>
          )}

          {internship.link && (
            <a
              href={internship.link}
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
