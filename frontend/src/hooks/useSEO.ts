import { useEffect } from 'react'

interface SEOConfig {
  title?: string
  description?: string
  canonical?: string
  noindex?: boolean
  ogTitle?: string
  ogDescription?: string
  ogImage?: string
}

const defaultConfig: SEOConfig = {
  title: 'Clarynt - Prompt Optimization for Marketing Agencies & Creative Studios',
  description: 'Clarynt is a prompt-optimization engine for marketing agencies and creative studios. Turn vague creative intent into repeatable, high-fidelity prompts with clarifying questions, prompt blueprints, quality checks, and a reusable prompt library.',
  canonical: 'https://app.clarynt.net/',
  noindex: false,
}

export function useSEO(config: SEOConfig = {}) {
  const mergedConfig = { ...defaultConfig, ...config }

  useEffect(() => {
    // Update title
    if (mergedConfig.title) {
      document.title = mergedConfig.title
    }

    // Update or create meta description
    let descMeta = document.querySelector('meta[name="description"]') as HTMLMetaElement
    if (!descMeta) {
      descMeta = document.createElement('meta')
      descMeta.name = 'description'
      document.head.appendChild(descMeta)
    }
    if (mergedConfig.description) {
      descMeta.content = mergedConfig.description
    }

    // Update or create canonical link
    let canonicalLink = document.querySelector('link[rel="canonical"]') as HTMLLinkElement
    if (!canonicalLink) {
      canonicalLink = document.createElement('link')
      canonicalLink.rel = 'canonical'
      document.head.appendChild(canonicalLink)
    }
    if (mergedConfig.canonical) {
      canonicalLink.href = mergedConfig.canonical
    }

    // Update or create robots meta
    let robotsMeta = document.querySelector('meta[name="robots"]') as HTMLMetaElement
    if (!robotsMeta) {
      robotsMeta = document.createElement('meta')
      robotsMeta.name = 'robots'
      document.head.appendChild(robotsMeta)
    }
    robotsMeta.content = mergedConfig.noindex
      ? 'noindex,nofollow'
      : 'index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1'

    // Update Open Graph tags
    const updateOGMeta = (property: string, content: string) => {
      let meta = document.querySelector(`meta[property="${property}"]`) as HTMLMetaElement
      if (!meta) {
        meta = document.createElement('meta')
        meta.setAttribute('property', property)
        document.head.appendChild(meta)
      }
      meta.content = content
    }

    if (mergedConfig.ogTitle || mergedConfig.title) {
      updateOGMeta('og:title', mergedConfig.ogTitle || mergedConfig.title || '')
    }
    if (mergedConfig.ogDescription || mergedConfig.description) {
      updateOGMeta('og:description', mergedConfig.ogDescription || mergedConfig.description || '')
    }
    if (mergedConfig.canonical) {
      updateOGMeta('og:url', mergedConfig.canonical)
    }
    if (mergedConfig.ogImage) {
      updateOGMeta('og:image', mergedConfig.ogImage)
    }

    // Update Twitter tags
    const updateTwitterMeta = (name: string, content: string) => {
      let meta = document.querySelector(`meta[name="${name}"]`) as HTMLMetaElement
      if (!meta) {
        meta = document.createElement('meta')
        meta.name = name
        document.head.appendChild(meta)
      }
      meta.content = content
    }

    if (mergedConfig.ogTitle || mergedConfig.title) {
      updateTwitterMeta('twitter:title', mergedConfig.ogTitle || mergedConfig.title || '')
    }
    if (mergedConfig.ogDescription || mergedConfig.description) {
      updateTwitterMeta('twitter:description', mergedConfig.ogDescription || mergedConfig.description || '')
    }
    if (mergedConfig.canonical) {
      updateTwitterMeta('twitter:url', mergedConfig.canonical)
    }
    if (mergedConfig.ogImage) {
      updateTwitterMeta('twitter:image', mergedConfig.ogImage)
    }
  }, [
    mergedConfig.title,
    mergedConfig.description,
    mergedConfig.canonical,
    mergedConfig.noindex,
    mergedConfig.ogTitle,
    mergedConfig.ogDescription,
    mergedConfig.ogImage,
  ])
}

// Pre-configured SEO hooks for common pages
export function useNoIndexSEO(title?: string) {
  useSEO({
    title: title || 'Clarynt',
    noindex: true,
  })
}
