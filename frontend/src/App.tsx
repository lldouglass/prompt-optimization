import { useEffect, useMemo, type ReactNode } from 'react'

const EMAIL = 'logandouglass7@gmail.com'
const EMAIL_SUBJECT = 'Clayrnt question'
const PHONE_DISPLAY = '720-391-4835'
const PHONE_LINK = 'tel:+17203914835'
const EMAIL_LINK = `mailto:${EMAIL}?subject=${encodeURIComponent(EMAIL_SUBJECT)}`

type Sample = {
  id: string
  title: string
  subtitle: string
  badge: string
  poster: string
  src: string
  tag: string
  note: string
}

const productSamples: Sample[] = [
  {
    id: 'jack-tall-owl',
    title: 'Tall Owl whipped tallow',
    subtitle: 'Animated premium skincare ad with a stronger character-led hook',
    badge: 'Featured sample',
    poster: '/jack-tall-owl-poster.jpg',
    src: '/jack-tall-owl.mp4',
    tag: 'Skincare',
    note:
      'A warmer character-led product ad. This is the lane for brands that want something more memorable than generic UGC or static product slides.',
  },
  {
    id: 'product-brand-sample',
    title: 'Pulse product sample',
    subtitle: 'Cleaner premium product reel for physical products',
    badge: 'Product-led',
    poster: '/product-brand-sample-poster.jpg',
    src: '/product-brand-sample.mp4',
    tag: 'Wellness',
    note:
      'This is the core premium product-brand lane, polished visuals, clear product focus, and no founder-on-camera dependency.',
  },
  {
    id: 'oral-care-sample',
    title: 'Oral-care sample',
    subtitle: 'Category-specific sample for tooth and oral-care brands',
    badge: 'Category proof',
    poster: '/dental-sample-poster.jpg',
    src: '/dental-sample.mp4',
    tag: 'Oral care',
    note:
      'A more tooth-specific example for brands that want to see relevant category proof right away.',
  },
]

const dentalSample: Sample = {
  id: 'dental-sample',
  title: 'Dental education sample',
  subtitle: 'Patient-education video built to help a practice look more helpful and trustworthy',
  badge: 'Dental sample',
  poster: '/dental-sample-poster.jpg',
  src: '/dental-sample.mp4',
  tag: 'Dental',
  note:
    'Useful for the dental lane, but the main Clayrnt landing page is now focused on product brands and premium short-form ads.',
}

function Shell({ children }: { children: ReactNode }) {
  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-950 text-slate-100">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(16,185,129,0.18),transparent_28%),radial-gradient(circle_at_85%_12%,rgba(14,165,233,0.18),transparent_24%),radial-gradient(circle_at_50%_100%,rgba(168,85,247,0.14),transparent_30%)]" />
      <div className="absolute inset-0 bg-[linear-gradient(to_bottom,rgba(15,23,42,0.3),rgba(2,6,23,0.92),rgba(2,6,23,1))]" />
      <div className="absolute inset-0 opacity-[0.08] [background-image:linear-gradient(rgba(148,163,184,0.16)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.16)_1px,transparent_1px)] [background-size:72px_72px]" />
      <div className="relative">{children}</div>
    </div>
  )
}

function Logo() {
  return (
    <div className="flex items-center gap-3">
      <img src="/clarynt_icon.jpg" alt="Clayrnt" className="h-10 w-10 rounded-2xl border border-white/10 object-cover shadow-lg shadow-emerald-950/40" />
      <div>
        <div className="text-lg font-semibold tracking-tight text-white">Clayrnt</div>
        <div className="text-xs uppercase tracking-[0.22em] text-slate-400">Premium short-form creative</div>
      </div>
    </div>
  )
}

function NavLink({ href, children }: { href: string; children: ReactNode }) {
  return (
    <a href={href} className="text-sm text-slate-300 transition hover:text-white">
      {children}
    </a>
  )
}

function PrimaryButton({ href, children }: { href: string; children: ReactNode }) {
  return (
    <a
      href={href}
      className="inline-flex items-center justify-center rounded-full bg-emerald-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-emerald-200"
    >
      {children}
    </a>
  )
}

function SecondaryButton({ href, children }: { href: string; children: ReactNode }) {
  return (
    <a
      href={href}
      className="inline-flex items-center justify-center rounded-full border border-white/12 bg-white/5 px-5 py-3 text-sm font-semibold text-white transition hover:border-white/20 hover:bg-white/10"
    >
      {children}
    </a>
  )
}

function TopBar() {
  return (
    <header className="sticky top-0 z-30 border-b border-white/10 bg-slate-950/70 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-6 py-4 sm:px-8 lg:px-10">
        <a href="/" className="min-w-0">
          <Logo />
        </a>
        <nav className="hidden items-center gap-7 lg:flex">
          <NavLink href="/#work">Work</NavLink>
          <NavLink href="/#process">How it works</NavLink>
          <NavLink href="/#why">Why Clayrnt</NavLink>
          <NavLink href="/brands">Samples</NavLink>
          <NavLink href="/dental">Dental</NavLink>
        </nav>
        <div className="flex items-center gap-3">
          <a href={EMAIL_LINK} className="hidden text-sm text-slate-300 transition hover:text-white sm:block">
            {EMAIL}
          </a>
          <PrimaryButton href="/brands">See samples</PrimaryButton>
        </div>
      </div>
    </header>
  )
}

function SectionIntro({ eyebrow, title, body }: { eyebrow: string; title: string; body: string }) {
  return (
    <div className="max-w-3xl">
      <div className="inline-flex items-center rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium uppercase tracking-[0.24em] text-emerald-200/90">
        {eyebrow}
      </div>
      <h2 className="mt-5 text-3xl font-semibold tracking-tight text-white sm:text-4xl">{title}</h2>
      <p className="mt-4 text-base leading-7 text-slate-300 sm:text-lg">{body}</p>
    </div>
  )
}

function SampleVideoCard({ sample, controls = true }: { sample: Sample; controls?: boolean }) {
  return (
    <article className="rounded-[30px] border border-white/10 bg-white/5 p-4 shadow-[0_30px_80px_rgba(2,6,23,0.45)] backdrop-blur">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="text-lg font-semibold text-white">{sample.title}</div>
          <div className="text-sm text-slate-400">{sample.subtitle}</div>
        </div>
        <div className="rounded-full border border-emerald-300/20 bg-emerald-300/10 px-3 py-1 text-xs font-medium text-emerald-200">
          {sample.badge}
        </div>
      </div>

      <div className="mb-4 flex flex-wrap items-center gap-2">
        <span className="rounded-full border border-white/10 bg-slate-950/80 px-3 py-1 text-xs text-slate-300">
          {sample.tag}
        </span>
        <span className="rounded-full border border-white/10 bg-slate-950/80 px-3 py-1 text-xs text-slate-400">
          Full quality on-page
        </span>
      </div>

      <div className="overflow-hidden rounded-[24px] border border-white/10 bg-black">
        <video
          className="aspect-[9/16] w-full bg-black object-cover"
          controls={controls}
          muted={!controls}
          loop={!controls}
          autoPlay={!controls}
          playsInline
          preload="metadata"
          poster={sample.poster}
        >
          <source src={sample.src} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      </div>

      <p className="mt-4 text-sm leading-6 text-slate-400">{sample.note}</p>
    </article>
  )
}

function ContactStrip({ note }: { note: string }) {
  return (
    <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="text-xl font-semibold text-white">Want to see if this fits your brand?</div>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">{note}</p>
        </div>
        <div className="flex flex-col gap-3 sm:flex-row">
          <PrimaryButton href={EMAIL_LINK}>Email Logan</PrimaryButton>
          <SecondaryButton href={PHONE_LINK}>Call or text Logan</SecondaryButton>
        </div>
      </div>
    </div>
  )
}

function LandingPage() {
  return (
    <main>
      <section className="mx-auto max-w-7xl px-6 pb-24 pt-12 sm:px-8 lg:px-10 lg:pb-28 lg:pt-16">
        <div className="grid gap-14 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
          <div>
            <div className="inline-flex items-center rounded-full border border-emerald-300/15 bg-emerald-300/10 px-4 py-2 text-xs font-medium uppercase tracking-[0.24em] text-emerald-100">
              Product brands, premium reels, proof first
            </div>

            <h1 className="mt-6 max-w-4xl text-5xl font-semibold tracking-tight text-white sm:text-6xl lg:text-7xl">
              Make the product feel expensive before someone ever clicks buy.
            </h1>

            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300 sm:text-xl">
              Clayrnt creates short-form ads and product reels for brands that need cleaner visuals,
              stronger hooks, and a more premium feel than generic filler content.
            </p>

            <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center">
              <PrimaryButton href="/brands">See the sample library</PrimaryButton>
              <SecondaryButton href={EMAIL_LINK}>Email Logan</SecondaryButton>
            </div>

            <div className="mt-8 grid gap-3 sm:grid-cols-3">
              {[
                ['Premium product look', 'Cleaner art direction and stronger visual polish.'],
                ['Multiple creative lanes', 'Product-led, character-led, and category-specific work.'],
                ['Small beta first', 'Start with proof, not a bloated retainer.'],
              ].map(([title, body]) => (
                <div key={title} className="rounded-3xl border border-white/10 bg-white/5 p-4 backdrop-blur">
                  <div className="text-sm font-semibold text-white">{title}</div>
                  <p className="mt-2 text-sm leading-6 text-slate-400">{body}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="relative">
            <div className="pointer-events-none absolute -inset-4 rounded-[36px] bg-[radial-gradient(circle_at_top,rgba(52,211,153,0.22),transparent_38%),radial-gradient(circle_at_bottom_right,rgba(59,130,246,0.18),transparent_32%)] blur-2xl" />
            <div className="relative rounded-[32px] border border-white/10 bg-slate-900/80 p-4 shadow-[0_30px_100px_rgba(2,6,23,0.65)] backdrop-blur xl:p-5">
              <div className="mb-4 flex items-center justify-between gap-3">
                <div>
                  <div className="text-sm font-semibold text-white">Featured sample</div>
                  <div className="text-sm text-slate-400">Real Clayrnt creative, not mock proof</div>
                </div>
                <div className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">
                  {productSamples[0].tag}
                </div>
              </div>

              <div className="overflow-hidden rounded-[26px] border border-white/10 bg-black">
                <video
                  className="aspect-[9/16] w-full bg-black object-cover"
                  autoPlay
                  muted
                  loop
                  playsInline
                  preload="metadata"
                  poster={productSamples[0].poster}
                >
                  <source src={productSamples[0].src} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>

              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
                  <div className="text-sm font-semibold text-white">Character-led lane</div>
                  <p className="mt-2 text-sm leading-6 text-slate-400">
                    Useful when the brand needs something warmer and more memorable than a simple product montage.
                  </p>
                </div>
                <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
                  <div className="text-sm font-semibold text-white">Proof-first workflow</div>
                  <p className="mt-2 text-sm leading-6 text-slate-400">
                    Start with sample work, pick the lane that feels strongest, then tighten the beta from there.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="work" className="mx-auto max-w-7xl px-6 py-20 sm:px-8 lg:px-10">
        <SectionIntro
          eyebrow="Real samples"
          title="Real work on the page, not a fake portfolio wall."
          body="The fastest way to judge Clayrnt is to look at the actual output. These are real sample assets already on the site, shown in full quality instead of compressed previews."
        />

        <div className="mt-10 grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
          <SampleVideoCard sample={productSamples[0]} />
          <div className="grid gap-6">
            {productSamples.slice(1).map((sample) => (
              <SampleVideoCard key={sample.id} sample={sample} />
            ))}
          </div>
        </div>
      </section>

      <section id="process" className="mx-auto max-w-7xl px-6 py-20 sm:px-8 lg:px-10">
        <SectionIntro
          eyebrow="How it works"
          title="Simple process, tighter output, less random guessing."
          body="This should feel lightweight. The goal is not to drag you into a giant agency process. The goal is to find the strongest creative lane fast and build from proof."
        />

        <div className="mt-10 grid gap-6 lg:grid-cols-3">
          {[
            {
              step: '01',
              title: 'Pick the angle',
              body: 'Start with the product, the customer, and the kind of reel you actually want to test first.',
            },
            {
              step: '02',
              title: 'Build the sample set',
              body: 'Clayrnt builds sample directions around real assets and product-specific hooks, not generic social filler.',
            },
            {
              step: '03',
              title: 'Use the strongest lane',
              body: 'Keep the lane that feels most premium and most believable, then iterate from there into a simple beta cadence.',
            },
          ].map((item) => (
            <div key={item.step} className="rounded-[30px] border border-white/10 bg-white/5 p-6 backdrop-blur">
              <div className="text-sm font-medium text-emerald-200">{item.step}</div>
              <div className="mt-3 text-2xl font-semibold text-white">{item.title}</div>
              <p className="mt-3 text-sm leading-7 text-slate-400">{item.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="why" className="mx-auto max-w-7xl px-6 py-20 sm:px-8 lg:px-10">
        <SectionIntro
          eyebrow="Why Clayrnt"
          title="Built for brands that want stronger visuals without pretending to be something else."
          body="The point is not to cosplay a giant ad platform. The point is to make the brand look better, faster, with real sample proof and a direct operator on the other side."
        />

        <div className="mt-10 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          {[
            {
              title: 'Premium visual direction',
              body: 'Cleaner lighting, framing, pacing, and presentation than the average low-trust social asset.',
            },
            {
              title: 'More than one creative lane',
              body: 'Product-led reels, character-led spots, and category-specific explainers can all live under one roof.',
            },
            {
              title: 'Proof-first sales motion',
              body: 'The page leads with real sample work because that is the fastest honest way to judge fit.',
            },
            {
              title: 'Direct contact with Logan',
              body: 'No fake sales team wall. If it feels close, you can just email, call, or text directly.',
            },
          ].map((item) => (
            <div key={item.title} className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
              <div className="text-lg font-semibold text-white">{item.title}</div>
              <p className="mt-3 text-sm leading-7 text-slate-400">{item.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-20 sm:px-8 lg:px-10">
        <ContactStrip note="If the samples feel close to the look you want, Logan can send one reel idea tailored to your product and talk through whether a small beta makes sense." />
      </section>

      <footer className="mx-auto max-w-7xl px-6 pb-16 pt-6 sm:px-8 lg:px-10">
        <div className="flex flex-col gap-6 rounded-[30px] border border-white/10 bg-white/5 p-6 backdrop-blur lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="text-lg font-semibold text-white">Clayrnt</div>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
              Premium short-form creative for brands that want cleaner visuals, stronger hooks, and a better first impression.
            </p>
          </div>
          <div className="flex flex-col gap-2 text-sm text-slate-300 sm:text-right">
            <a href={EMAIL_LINK} className="transition hover:text-white">
              {EMAIL}
            </a>
            <a href={PHONE_LINK} className="transition hover:text-white">
              {PHONE_DISPLAY}
            </a>
            <a href="/brands" className="transition hover:text-white">
              View sample library
            </a>
          </div>
        </div>
      </footer>
    </main>
  )
}

function BrandsPage() {
  const featuredSample = productSamples[0]
  const librarySamples = productSamples.slice(1)

  return (
    <main className="mx-auto max-w-7xl px-6 py-12 sm:px-8 lg:px-10 lg:py-16">
      <section className="grid gap-12 lg:grid-cols-[1.02fr_0.98fr] lg:items-start">
        <div>
          <div className="inline-flex items-center rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium uppercase tracking-[0.24em] text-emerald-200">
            Sample library
          </div>
          <h1 className="mt-5 max-w-4xl text-4xl font-semibold tracking-tight text-white sm:text-5xl lg:text-6xl">
            Short-form product ads that feel clean, premium, and built for real brands.
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-300">
            This page is a live library for the Clayrnt product-brand lane. As stronger work lands, it can keep growing without turning into a messy one-off page.
          </p>

          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            {[
              {
                title: 'Premium visual style',
                body: 'Built to feel more like a product ad than a filler social post.',
              },
              {
                title: 'Multiple creative lanes',
                body: 'Product-led, character-led, and category-specific work can all live here.',
              },
              {
                title: 'Simple beta first',
                body: 'Start with a few tailored samples before a bigger monthly cadence.',
              },
            ].map((item) => (
              <div key={item.title} className="rounded-3xl border border-white/10 bg-white/5 p-4 backdrop-blur">
                <div className="text-sm font-semibold text-white">{item.title}</div>
                <p className="mt-2 text-sm leading-6 text-slate-400">{item.body}</p>
              </div>
            ))}
          </div>

          <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center">
            <PrimaryButton href="#featured-sample">Watch the featured sample</PrimaryButton>
            <SecondaryButton href="#sample-library">Browse the library</SecondaryButton>
          </div>

          <div className="mt-8 rounded-[28px] border border-white/10 bg-white/5 p-5 backdrop-blur">
            <div className="text-sm font-semibold text-white">Direct contact</div>
            <div className="mt-3 space-y-2 text-sm leading-6 text-slate-300">
              <div>
                <span className="text-slate-500">Email:</span>{' '}
                <a href={EMAIL_LINK} className="font-medium text-emerald-200 transition hover:text-emerald-100">
                  {EMAIL}
                </a>
              </div>
              <div>
                <span className="text-slate-500">Phone:</span>{' '}
                <a href={PHONE_LINK} className="font-medium text-emerald-200 transition hover:text-emerald-100">
                  {PHONE_DISPLAY}
                </a>
              </div>
              <div className="text-slate-500">
                If this looks useful, Logan can send one reel idea tailored to your product.
              </div>
            </div>
          </div>
        </div>

        <section id="featured-sample">
          <SampleVideoCard sample={featuredSample} />
        </section>
      </section>

      <section id="sample-library" className="mt-12">
        <div className="mb-6 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <div className="text-sm font-semibold text-white">More samples</div>
            <div className="text-sm text-slate-400">
              Add new work by dropping in a file and extending the sample list.
            </div>
          </div>
          <div className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-400">
            Scalable layout for future proof
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {librarySamples.map((sample) => (
            <SampleVideoCard key={sample.id} sample={sample} />
          ))}
        </div>
      </section>
    </main>
  )
}

function DentalPage() {
  return (
    <main className="mx-auto max-w-7xl px-6 py-12 sm:px-8 lg:px-10 lg:py-16">
      <section className="grid gap-12 lg:grid-cols-[1.02fr_0.98fr] lg:items-center">
        <div>
          <div className="inline-flex items-center rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium uppercase tracking-[0.24em] text-emerald-200">
            Dental sample
          </div>
          <h1 className="mt-5 max-w-3xl text-4xl font-semibold tracking-tight text-white sm:text-5xl lg:text-6xl">
            Patient-education videos that help dental offices build trust online.
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-300">
            This is the original dental sample lane. It stays here as proof for practices, while the main Clayrnt landing page now leads with the broader product-brand offer.
          </p>

          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            {[
              {
                title: 'Build trust early',
                body: 'Useful when someone is checking out the office before they ever book.',
              },
              {
                title: 'Answer common questions',
                body: 'Content built around patient concerns instead of random filler.',
              },
              {
                title: 'Keep it lightweight',
                body: 'Start with a simple test before committing to a bigger retainer.',
              },
            ].map((item) => (
              <div key={item.title} className="rounded-3xl border border-white/10 bg-white/5 p-4 backdrop-blur">
                <div className="text-sm font-semibold text-white">{item.title}</div>
                <p className="mt-2 text-sm leading-6 text-slate-400">{item.body}</p>
              </div>
            ))}
          </div>

          <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center">
            <PrimaryButton href={EMAIL_LINK}>Email Logan</PrimaryButton>
            <SecondaryButton href={PHONE_LINK}>Call or text Logan</SecondaryButton>
          </div>
        </div>

        <SampleVideoCard sample={dentalSample} />
      </section>
    </main>
  )
}

export default function App() {
  const pathname = window.location.pathname.toLowerCase()
  const isBrands = pathname.startsWith('/brands') || pathname.startsWith('/products')
  const isDental = pathname.startsWith('/dental')

  const meta = useMemo(() => {
    if (isBrands) {
      return {
        title: 'Clayrnt | Product Brand Reels',
        description:
          'Premium short-form product ads and sample reels for brands that want cleaner visuals, stronger hooks, and a higher-trust first impression.',
      }
    }

    if (isDental) {
      return {
        title: 'Clayrnt | Dental Sample',
        description:
          'Patient-education videos that help dental offices build trust with potential patients online.',
      }
    }

    return {
      title: 'Clayrnt | Premium Short-Form Creative',
      description:
        'Clayrnt creates premium short-form ads and product reels for brands that want cleaner visuals, stronger hooks, and proof-first creative.',
    }
  }, [isBrands, isDental])

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
    <Shell>
      <TopBar />
      {isBrands ? <BrandsPage /> : isDental ? <DentalPage /> : <LandingPage />}
    </Shell>
  )
}
