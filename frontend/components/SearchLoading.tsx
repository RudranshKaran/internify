'use client'

import { useState, useEffect, useRef } from 'react'

const MESSAGES = [
  "Scanning the web for your next opportunity...",
  "Matching your skills to open roles...",
  "Finding companies that need someone exactly like you...",
  "Every great career started with one cold email.",
  "Looking for roles aligned with your experience...",
  "Your next internship is out there. We're finding it.",
  "Cross-referencing your resume with live listings...",
  "The best time to apply was yesterday. The second best time is now.",
  "Digging through company pages so you don't have to...",
  "Somewhere out there, a hiring manager is waiting for your email.",
  "Prioritizing the most relevant matches for you...",
  "Great opportunities often hide in plain sight. We're uncovering them.",
]

export default function SearchLoading() {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [fadeState, setFadeState] = useState<'visible' | 'hidden'>('visible')
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    intervalRef.current = setInterval(() => {
      // Start fade-out
      setFadeState('hidden')

      // After fade completes, swap message and fade back in
      timeoutRef.current = setTimeout(() => {
        setCurrentIndex((prev) => (prev + 1) % MESSAGES.length)
        setFadeState('visible')
      }, 400) // matches transition duration
    }, 3000)

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
    }
  }, [])

  return (
    <div className="flex flex-col items-center justify-center py-16 space-y-6">
      {/* Message with fade transition */}
      <div className="h-12 flex items-center justify-center">
        <p
          key={currentIndex}
          className="text-base text-gray-600 text-center max-w-md transition-opacity duration-400"
          style={{
            opacity: fadeState === 'visible' ? 1 : 0,
            transitionDuration: '400ms',
          }}
        >
          {MESSAGES[currentIndex]}
        </p>
      </div>

      {/* Typing indicator dots */}
      <div className="flex items-center space-x-1.5">
        <span
          className="w-2 h-2 rounded-full bg-primary"
          style={{
            animation: 'pulse-dot 1.4s infinite',
            animationDelay: '0s',
          }}
        />
        <span
          className="w-2 h-2 rounded-full bg-primary"
          style={{
            animation: 'pulse-dot 1.4s infinite',
            animationDelay: '0.2s',
          }}
        />
        <span
          className="w-2 h-2 rounded-full bg-primary"
          style={{
            animation: 'pulse-dot 1.4s infinite',
            animationDelay: '0.4s',
          }}
        />
      </div>
    </div>
  )
}
