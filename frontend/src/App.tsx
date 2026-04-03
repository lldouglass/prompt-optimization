import { useEffect, useMemo } from 'react'

const EMAIL = 'logandouglass7@gmail.com'
const EMAIL_SUBJECT = 'Content question'
const PHONE_DISPLAY = '720-391-4835'
const PHONE_LINK = 'tel:+17203914835'

function Header() {
  const emailHref = `mailto:${EMAIL}?subject=${encodeURIComponent(EMAIL_SUBJECT)}`

  return (
    <header className="mb-10 flex items-center justify-between gap-4">
      <div>
        <div className="text-xs font-semibold uppercase tracking-[0.3em] text-emerald-300/80">
          Clayrnt
        </div>
        <div className="mt-2 text-sm text-slate-400">Short-form sample pages</div>
      </div>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <a
          href={PHONE_LINK}
          className="rounded-full border border-slate-700 px-4 py-2 text-sm font-medium text-slate-100 transition hover:border-slate-500 hover:bg-slate-900"
        >
          Call Logan
        </a>
        <a
          href={emailHref}
          className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-4 py-2 text-sm font-medium text-emerald-200 transition hover:border-emerald-300/50 hover:bg-emerald-400/15"
        >
          Email Logan
        </a>
      </div>
    </header>
  )
}

function ContactCard({ note }: { note: string }) {
  const emailHref = `mailto:${EMAIL}?subject=${encodeURIComponent(EMAIL_SUBJECT)}`

  return (
    <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
      <div className="text-sm font-semibold text-white">Contact</div>
      <div className="mt-3 space-y-2 text-sm leading-6 text-slate-300">
        <div>
          <span className="text-slate-500">Email:</span>{' '}
          <a
            className="font-medium text-emerald-200 underline decoration-emerald-400/30 underline-offset-4"
            href={emailHref}
          >
            {EMAIL}
          </a>
        </div>
        <div>
          <span className="text-slate-500">Phone:</span>{' '}
          <a
            className="font-medium text-emerald-200 underline decoration-emerald-400/30 underline-offset-4"
            href={PHONE_LINK}
          >
            {PHONE_DISPLAY}
          </a>
        </div>
        <div className="text-slate-500">{note}</div>
      </div>
    </div>
  )
}

function DentalPage() {
  const emailHref = `mailto:${EMAIL}?subject=${encodeURIComponent('Dental sample video question')}`

  return (
    <main className="grid flex-1 gap-10 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
      <section>
        <div className="inline-flex items-center rounded-full border border-slate-800 bg-slate-900 px-3 py-1 text-xs text-slate-300">
          Help potential patients trust your office before they book
        </div>

        <h1 className="mt-5 max-w-3xl text-4xl font-semibold tracking-tight text-white sm:text-5xl lg:text-6xl">
          Patient-education videos that help dental offices build trust online
        </h1>

        <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-300">
          I make simple patient-education videos that help dental offices build trust with
          potential patients online.
        </p>

        <div className="mt-8 grid gap-4 sm:grid-cols-3">
          {[
            {
              title: 'Build trust before the first visit',
              body: 'Simple patient-education videos help the office look more helpful and trustworthy when someone checks you out online.',
            },
            {
              title: 'Answer the questions patients already have',
              body: 'The content is built around common patient concerns, not random filler just to keep a feed busy.',
            },
            {
              title: 'Start with a simple 30-day beta',
              body: 'The goal is a small low-risk test first, not a giant agency retainer out of the gate.',
            },
          ].map((item) => (
            <div
              key={item.title}
              className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4 shadow-[0_0_0_1px_rgba(255,255,255,0.02)]"
            >
              <div className="text-sm font-semibold text-white">{item.title}</div>
              <p className="mt-2 text-sm leading-6 text-slate-400">{item.body}</p>
            </div>
          ))}
        </div>

        <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center">
          <a
            href="#sample-video"
            className="inline-flex items-center justify-center rounded-full bg-emerald-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-emerald-300"
          >
            Watch the sample
          </a>
          <a
            href={emailHref}
            className="inline-flex items-center justify-center rounded-full border border-slate-700 px-5 py-3 text-sm font-semibold text-slate-100 transition hover:border-slate-500 hover:bg-slate-900"
          >
            Email Logan
          </a>
        </div>

        <ContactCard note="If this looks useful, reply to the email you received or call/text directly." />
      </section>

      <section
        id="sample-video"
        className="rounded-[28px] border border-slate-800 bg-slate-900/80 p-4 shadow-2xl shadow-black/25 sm:p-5"
      >
        <div className="mb-4 flex items-center justify-between gap-3">
          <div>
            <div className="text-sm font-semibold text-white">Sample video</div>
            <div className="text-sm text-slate-400">A quick example of the content format</div>
          </div>
          <div className="rounded-full border border-slate-800 bg-slate-950 px-3 py-1 text-xs text-slate-400">
            Full quality on-page
          </div>
        </div>

        <div className="overflow-hidden rounded-[24px] border border-slate-800 bg-black">
          <video
            className="aspect-[9/16] w-full bg-black object-cover"
            controls
            preload="metadata"
            poster="/dental-sample-poster.jpg"
          >
            <source src="/dental-sample.mp4" type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </div>

        <div className="mt-4 rounded-2xl border border-slate-800 bg-slate-950/70 p-4 text-sm leading-6 text-slate-400">
          This page is intentionally simple. The point is just to show the content clearly,
          in full quality, without the weird compression and low-trust preview issues that
          can happen inside email.
        </div>
      </section>
    </main>
  )
}

function BrandsPage() {
  const emailHref = `mailto:${EMAIL}?subject=${encodeURIComponent('1 reel idea for my product')}`
  const samples = [
    {
      id: 'product-brand-sample',
      title: 'Product-brand sample',
      subtitle: 'A premium-style example for physical products',
      badge: 'Website review cut',
      poster: '/product-brand-sample-poster.jpg',
      src: '/product-brand-sample.mp4',
      note:
        'This is the main product-brand lane: premium visuals, clear product focus, and no founder-on-camera dependency.',
    },
    {
      id: 'oral-care-sample',
      title: 'Oral-care sample',
      subtitle: 'Relevant proof for tooth and oral-care products',
      badge: 'Tooth sample',
      poster: '/dental-sample-poster.jpg',
      src: '/dental-sample.mp4',
      note:
        'Included here as a second sample for oral-care brands that want to see a more tooth-specific example without leaving the product-brand page.',
    },
  ]

  return (
    <main className="grid flex-1 gap-10 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
      <section>
        <div className="inline-flex items-center rounded-full border border-slate-800 bg-slate-900 px-3 py-1 text-xs text-slate-300">
          Product brands
        </div>

        <h1 className="mt-5 max-w-3xl text-4xl font-semibold tracking-tight text-white sm:text-5xl lg:text-6xl">
          Premium short form product videos
        </h1>

        <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-300">
          This is the kind of product-focused reel I can make for brands that want cleaner,
          more premium social content without getting the founder on camera every week.
        </p>

        <div className="mt-8 grid gap-4 sm:grid-cols-3">
          {[
            {
              title: 'Premium visual style',
              body: 'Designed to feel more like a product ad than a throwaway social post.',
            },
            {
              title: 'No founder filming needed',
              body: 'Useful for brands that want consistent content without recording new footage every week.',
            },
            {
              title: 'Simple beta first',
              body: 'Start with a few tailored samples before committing to a bigger monthly cadence.',
            },
          ].map((item) => (
            <div
              key={item.title}
              className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4 shadow-[0_0_0_1px_rgba(255,255,255,0.02)]"
            >
              <div className="text-sm font-semibold text-white">{item.title}</div>
              <p className="mt-2 text-sm leading-6 text-slate-400">{item.body}</p>
            </div>
          ))}
        </div>

        <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center">
          <a
            href="#sample-gallery"
            className="inline-flex items-center justify-center rounded-full bg-emerald-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-emerald-300"
          >
            Watch the samples
          </a>
          <a
            href={emailHref}
            className="inline-flex items-center justify-center rounded-full border border-slate-700 px-5 py-3 text-sm font-semibold text-slate-100 transition hover:border-slate-500 hover:bg-slate-900"
          >
            Email Logan
          </a>
        </div>

        <ContactCard note="If this looks useful, reply and Logan can send 1 reel idea tailored to your product. Oral-care brands can review the second tooth-specific sample below too." />
      </section>

      <section
        id="sample-gallery"
        className="rounded-[28px] border border-slate-800 bg-slate-900/80 p-4 shadow-2xl shadow-black/25 sm:p-5"
      >
        <div className="mb-4 flex items-center justify-between gap-3">
          <div>
            <div className="text-sm font-semibold text-white">Sample gallery</div>
            <div className="text-sm text-slate-400">Product-brand proof first, with an extra oral-care sample for tooth-related brands</div>
          </div>
          <div className="rounded-full border border-slate-800 bg-slate-950 px-3 py-1 text-xs text-slate-400">
            Full quality on-page
          </div>
        </div>

        <div className="grid gap-5">
          {samples.map((sample) => (
            <div
              key={sample.id}
              className="rounded-[24px] border border-slate-800 bg-slate-950/70 p-3 sm:p-4"
            >
              <div className="mb-3 flex items-center justify-between gap-3">
                <div>
                  <div className="text-sm font-semibold text-white">{sample.title}</div>
                  <div className="text-sm text-slate-400">{sample.subtitle}</div>
                </div>
                <div className="rounded-full border border-slate-800 bg-black px-3 py-1 text-xs text-slate-400">
                  {sample.badge}
                </div>
              </div>

              <div className="overflow-hidden rounded-[20px] border border-slate-800 bg-black">
                <video
                  className="aspect-[9/16] w-full bg-black object-cover"
                  controls
                  preload="metadata"
                  poster={sample.poster}
                >
                  <source src={sample.src} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>

              <div className="mt-3 text-sm leading-6 text-slate-400">{sample.note}</div>
            </div>
          ))}
        </div>

        <div className="mt-4 rounded-2xl border border-slate-800 bg-slate-950/70 p-4 text-sm leading-6 text-slate-400">
          This page stays intentionally simple. The goal is to show strong examples clearly,
          in full quality, without burying them under agency fluff.
        </div>
      </section>
    </main>
  )
}

export default function App() {
  const pathname = window.location.pathname
  const isBrands = pathname.startsWith('/brands') || pathname.startsWith('/products')

  const meta = useMemo(() => {
    if (isBrands) {
      return {
        title: 'Clayrnt | Product Brand Reels',
        description:
          'Short-form reels for product brands that need better content ideas, stronger hooks, and cleaner demo angles.',
      }
    }

    return {
      title: 'Clayrnt | Dental Sample',
      description:
        'Simple patient-education videos that help dental offices build trust with potential patients online.',
    }
  }, [isBrands])

  useEffect(() => {
    document.title = meta.title

    let descriptionMeta = document.querySelector('meta[name="description"]')
    if (!descriptionMeta) {
      descriptionMeta = document.createElement('meta')
      descriptionMeta.setAttribute('name', 'description')
      document.head.appendChild(descriptionMeta)
    }
    descriptionMeta.setAttribute('content', meta.description)
  }, [meta])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex min-h-screen max-w-6xl flex-col px-6 py-10 sm:px-8 lg:px-10">
        <Header />
        {isBrands ? <BrandsPage /> : <DentalPage />}
      </div>
    </div>
  )
}
