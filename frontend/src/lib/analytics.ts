import posthog from 'posthog-js'

// Initialize PostHog - only in production or if explicitly enabled
const POSTHOG_KEY = import.meta.env.VITE_POSTHOG_KEY
const POSTHOG_HOST = import.meta.env.VITE_POSTHOG_HOST || 'https://us.i.posthog.com'

let initialized = false

export function initAnalytics() {
  if (initialized || !POSTHOG_KEY) {
    return
  }

  posthog.init(POSTHOG_KEY, {
    api_host: POSTHOG_HOST,
    // Capture pageviews automatically
    capture_pageview: true,
    // Capture link clicks
    capture_pageleave: true,
    // Disable in development unless explicitly enabled
    loaded: (posthog) => {
      if (import.meta.env.DEV && !import.meta.env.VITE_POSTHOG_KEY) {
        posthog.opt_out_capturing()
      }
    }
  })

  initialized = true
}

// Track custom events
export function track(event: string, properties?: Record<string, unknown>) {
  if (!POSTHOG_KEY) {
    // Log to console in development
    if (import.meta.env.DEV) {
      console.log('[Analytics]', event, properties)
    }
    return
  }
  posthog.capture(event, properties)
}

// Identify user after login/signup
export function identify(userId: string, traits?: Record<string, unknown>) {
  if (!POSTHOG_KEY) {
    if (import.meta.env.DEV) {
      console.log('[Analytics] Identify:', userId, traits)
    }
    return
  }
  posthog.identify(userId, traits)
}

// Reset on logout
export function resetAnalytics() {
  if (!POSTHOG_KEY) return
  posthog.reset()
}

// Key events to track:
// 1. signup_completed - User successfully registered
// 2. optimization_started - User clicked optimize button
// 3. optimization_completed - Optimization finished with scores
// 4. prompt_copied - User copied optimized prompt
// 5. upgrade_clicked - User initiated checkout
