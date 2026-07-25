'use client'

import { useState, useEffect, useRef } from 'react'

const LOADING_MESSAGES = [
  "Analyzing your resume and the job description...",
  "Crafting a compelling opening paragraph...",
  "Highlighting your most relevant skills and experience...",
  "Personalizing the email to make it stand out...",
  "Polishing the tone to strike the right balance...",
  "Adding specific achievements that match the role...",
  "Fine-tuning the subject line for maximum impact...",
  "Making sure every sentence adds value...",
  "You miss 100% of the opportunities you don't apply for.",
  "Almost there — formatting the final draft...",
]

const ERROR_MESSAGES: Record<string, string> = {
  401: "Your session has expired. Please log in again.",
  402: "AI credits exhausted. Please top up to continue generating emails.",
  404: "No resume found. Please upload a resume first.",
  413: "Resume or job description is too long. Try a shorter version.",
  422: "Could not process the email request. The data may be incomplete.",
  429: "Too many requests. Please wait a moment and try again.",
  502: "The AI service is temporarily unavailable. Please try again in a few moments.",
  503: "The server is busy. Please try again shortly.",
}

interface EmailGenerationLoadingProps {
  error?: {
    status?: number
    message: string
  } | null
  onRetry?: () => void
  onBack?: () => void
}

export default function EmailGenerationLoading({
  error,
  onRetry,
  onBack,
}: EmailGenerationLoadingProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [fadeState, setFadeState] = useState<'visible' | 'hidden'>('visible')
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    intervalRef.current = setInterval(() => {
      setFadeState('hidden')
      timeoutRef.current = setTimeout(() => {
        setCurrentIndex((prev) => (prev + 1) % LOADING_MESSAGES.length)
        setFadeState('visible')
      }, 400)
    }, 3000)

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
    }
  }, [])

  // Error state
  if (error) {
    const friendlyMessage =
      ERROR_MESSAGES[error.status ?? ''] ||
      (error.message?.toLowerCase().includes('resume')
        ? ERROR_MESSAGES[404]
        : error.message?.toLowerCase().includes('credit') ||
            error.message?.toLowerCase().includes('quota')
          ? ERROR_MESSAGES[402]
          : error.message?.toLowerCase().includes('too many')
            ? 'You have reached the rate limit. Please wait a moment and try again.'
            : null)

    return (
      <div className="flex flex-col items-center justify-center py-16 space-y-6">
        {/* Error icon */}
        <div className="relative">
          <div className="w-20 h-20 rounded-full bg-red-50 border-2 border-red-200 flex items-center justify-center">
            <svg
              className="w-10 h-10 text-red-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
              />
            </svg>
          </div>
        </div>

        {/* Error message */}
        <div className="text-center max-w-md space-y-2">
          <h3 className="text-lg font-semibold text-red-700">
            Could not generate email
          </h3>
          <p className="text-sm text-red-600">
            {friendlyMessage || error.message}
          </p>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-3">
          {onRetry && (
            <button
              onClick={onRetry}
              className="px-5 py-2.5 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors font-medium flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              Try Again
            </button>
          )}
          {onBack && (
            <button
              onClick={onBack}
              className="px-5 py-2.5 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              Back to Dashboard
            </button>
          )}
        </div>
      </div>
    )
  }

  // Loading state
  return (
    <div className="flex flex-col items-center justify-center py-16 space-y-8">
      {/* Animated envelope */}
      <div className="relative">
        <div className="w-24 h-24 rounded-2xl bg-primary/5 border-2 border-primary/20 flex items-center justify-center animate-bounce">
          <svg
            className="w-12 h-12 text-primary"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75"
            />
          </svg>
        </div>
        {/* Spinning ring behind */}
        <div className="absolute -inset-3 rounded-full border-2 border-primary/20 border-t-primary animate-spin" />
      </div>

      {/* Rotating message */}
      <div className="h-14 flex items-center justify-center">
        <p
          key={currentIndex}
          className="text-base text-gray-600 text-center max-w-md leading-relaxed"
          style={{
            opacity: fadeState === 'visible' ? 1 : 0,
            transition: 'opacity 400ms ease-in-out',
          }}
        >
          {LOADING_MESSAGES[currentIndex]}
        </p>
      </div>

      {/* Pulsing dots */}
      <div className="flex items-center space-x-2">
        <span
          className="w-2.5 h-2.5 rounded-full bg-primary/60"
          style={{
            animation: 'pulse-dot 1.4s ease-in-out infinite',
            animationDelay: '0s',
          }}
        />
        <span
          className="w-2.5 h-2.5 rounded-full bg-primary/60"
          style={{
            animation: 'pulse-dot 1.4s ease-in-out infinite',
            animationDelay: '0.2s',
          }}
        />
        <span
          className="w-2.5 h-2.5 rounded-full bg-primary/60"
          style={{
            animation: 'pulse-dot 1.4s ease-in-out infinite',
            animationDelay: '0.4s',
          }}
        />
      </div>
    </div>
  )
}
