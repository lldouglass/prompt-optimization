import { useEffect, useMemo, type ReactNode } from 'react'

const EMAIL = 'logandouglass7@gmail.com'
const EMAIL_SUBJECT = 'Clarynt question'
const PHONE_DISPLAY = '720-391-4835'
const PHONE_LINK = 'tel:+17203914835'
const EMAIL_LINK = `mailto:${EMAIL}?subject=${encodeURIComponent(EMAIL_SUBJECT)}`
const BOOK_CALL_LINK = 'https://cal.com/logan-douglass-isjf9m/intro-call'

type Sample = {
  id: string
  title: string
  subtitle: string
  badge: string
  poster?: string
  src: string
  tag: string
  note: string
}

const productSamples: Sample[] = [
  {
    id: 'jack-tall-owl',
    title: 'Tall Owl whipped tallow',
    subtitle: 'Vanilla orange apothecary product story',
    badge: 'Featured',
    poster: '/jack-tall-owl-poster.jpg',
    src: '/jack-tall-owl.mp4',
    tag: 'Skincare',
    note:
      'A warmer handcrafted skincare lane that moves from world-building into the product and jar reveal instead of feeling like a generic product spin.',
  },
  {
    id: 'tall-owl-plain-ad',
    title: 'Tall Owl plain ad',
    subtitle: 'Clean vanilla orange skincare pitch',
    badge: 'Product ad',
    poster: '/tall-owl-plain-ad-poster.jpg',
    src: '/tall-owl-plain-ad.mp4',
    tag: 'Skincare',
    note:
      'A cleaner direct-response Tall Owl lane built around the jar, whipped texture, short ingredient list, and calm-skin positioning.',
  },
  {
    id: 'product-brand-sample',
    title: 'Pulse product reel',
    subtitle: 'Clean premium reel for physical products',
    badge: 'Core lane',
    poster: '/product-brand-sample-poster.jpg',
    src: '/product-brand-sample.mp4',
    tag: 'Product reel',
    note:
      'A polished product-first lane with clean visuals, direct product focus, and no founder-on-camera dependency.',
  },
  {
    id: 'atlas-daily-one-shot',
    title: 'Atlas Daily one-shot',
    subtitle: 'Simple one-shot for DTC-style testing',
    badge: 'One-shot',
    src: '/atlas-daily-one-shot.mp4',
    tag: 'One-shot',
    note:
      'A compact creative direction for brands that want clean visuals and quick concept testing.',
  },
  {
    id: 'atlas-daily-action-v2',
    title: 'Atlas Daily motion reel',
    subtitle: 'More movement, stronger ad energy',
    badge: 'Motion lane',
    src: '/atlas-daily-action-v2.mp4',
    tag: 'Action',
    note:
      'A more active variation when a brand needs extra pace and commercial energy without losing polish.',
  },
  {
    id: 'arc-one-shot',
    title: 'Arc one-shot',
    subtitle: 'Minimal product vignette with premium framing',
    badge: 'One-shot',
    src: '/arc-one-shot.mp4',
    tag: 'Minimal',
    note:
      'Useful for product pages, paid social, or a clean premium visual before heavier story work.',
  },
  {
    id: 'arc-action-v2',
    title: 'Arc motion reel',
    subtitle: 'Sharper motion-first product direction',
    badge: 'Motion lane',
    src: '/arc-action-v2.mp4',
    tag: 'Motion',
    note:
      'Adds pace and movement while keeping the product presentation controlled.',
  },
  {
    id: 'arc-two-shot-micro-ad',
    title: 'Arc two-shot micro ad',
    subtitle: 'Short premium concept with stronger campaign feel',
    badge: 'Micro ad',
    src: '/arc-two-shot-micro-ad.mp4',
    tag: 'Campaign',
    note:
      'Closer to a mini paid-social concept than a simple product turntable or isolated one-shot.',
  },
  {
    id: 'luma-one-shot',
    title: 'Luma editorial one-shot',
    subtitle: 'Editorial one-shot direction for premium brands',
    badge: 'Editorial',
    src: '/luma-one-shot.mp4',
    tag: 'Editorial',
    note:
      'A clean editorial lane for brands that want something elevated without overcomplicating the creative.',
  },
  {
    id: 'luma-action-v2',
    title: 'Luma motion reel',
    subtitle: 'Faster pacing with a high-end visual finish',
    badge: 'Motion lane',
    src: '/luma-action-v2.mp4',
    tag: 'Pacing',
    note:
      'Built for brands that need more urgency and motion while keeping the overall piece polished.',
  },
  {
    id: 'gurunanda-monk',
    title: 'GuruNanda character concept',
    subtitle: 'Brand character concept with stronger identity',
    badge: 'Character lane',
    poster: '/gurunanda-monk-poster.jpg',
    src: '/gurunanda-monk.mp4',
    tag: 'Character',
    note:
      'A stronger brand-character direction when the goal is memorability instead of a purely clinical product reel.',
  },
  {
    id: 'gurunanda-monk-spec',
    title: 'GuruNanda campaign concept',
    subtitle: 'Campaign-style brand concept with more polish',
    badge: 'Campaign concept',
    poster: '/gurunanda-monk-poster.jpg',
    src: '/gurunanda-monk-spec.mp4',
    tag: 'Campaign',
    note:
      'A more campaign-shaped direction for brands that want the sample to feel less like an isolated product reel.',
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
    'A focused proof point for educational dental content when a practice wants a patient-facing sample before a broader campaign.',
}

const sampleMap = Object.fromEntries(productSamples.map((sample) => [sample.id, sample])) as Record<string, Sample>

function getSample(id: string) {
  return sampleMap[id]
}

function Shell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="relative isolate min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top,rgba(34,197,94,0.08),transparent_20%),radial-gradient(circle_at_80%_10%,rgba(99,102,241,0.16),transparent_24%),linear-gradient(180deg,#030712_0%,#050816_38%,#070b18_100%)]">
        <div className="pointer-events-none absolute inset-0 opacity-[0.06] [background-image:linear-gradient(rgba(255,255,255,0.24)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.24)_1px,transparent_1px)] [background-size:72px_72px]" />
        {children}
      </div>
    </div>
  )
}

function Logo({ tone = 'dark' }: { tone?: 'dark' | 'light' }) {
  const isLight = tone === 'light'

  return (
    <div className="flex items-center gap-3">
      <img
        src="/clarynt_icon.jpg"
        alt="Clarynt"
        className={[
          'h-10 w-10 rounded-lg object-cover shadow-lg shadow-emerald-950/40',
          isLight ? 'border border-slate-200' : 'border border-white/10',
        ].join(' ')}
      />
      <div>
        <div className={['text-lg font-semibold tracking-tight', isLight ? 'text-slate-950' : 'text-white'].join(' ')}>
          Clarynt
        </div>
        <div className={['hidden text-[11px] uppercase tracking-[0.24em] sm:block', isLight ? 'text-slate-500' : 'text-slate-400'].join(' ')}>
          Premium short-form creative
        </div>
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
      className="inline-flex items-center justify-center rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200"
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
    <header className="sticky top-0 z-40 border-b border-white/8 bg-slate-950/70 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-6 py-4 sm:px-8 lg:px-10">
        <a href="/" className="min-w-0">
          <Logo />
        </a>
        <nav className="hidden items-center gap-7 lg:flex">
          <NavLink href="/#work">Work</NavLink>
          <NavLink href="/#capabilities">Capabilities</NavLink>
          <NavLink href="/#process">Process</NavLink>
          <NavLink href="/brands">Library</NavLink>
        </nav>
        <div className="flex items-center gap-3">
          <SecondaryButton href={BOOK_CALL_LINK}>Book a call</SecondaryButton>
        </div>
      </div>
    </header>
  )
}

function AutoVideo({ sample, className = '', tone = 'dark' }: { sample: Sample; className?: string; tone?: 'dark' | 'light' }) {
  return (
    <article
      className={[
        'group relative overflow-hidden rounded-[28px] border shadow-[0_20px_60px_rgba(15,23,42,0.18)]',
        tone === 'dark' ? 'border-white/10 bg-white/5 backdrop-blur-xl' : 'border-slate-200 bg-white',
        className,
      ].join(' ')}
    >
      <div className="absolute inset-x-0 top-0 z-10 flex items-center justify-between px-4 pt-4">
        <div
          className={[
            'rounded-full px-3 py-1 text-[11px] font-medium uppercase tracking-[0.22em]',
            tone === 'dark'
              ? 'border border-white/12 bg-slate-950/70 text-slate-200'
              : 'border border-slate-200 bg-white/90 text-slate-700',
          ].join(' ')}
        >
          {sample.badge}
        </div>
        <div
          className={[
            'rounded-full px-3 py-1 text-[11px] font-medium',
            tone === 'dark'
              ? 'border border-white/12 bg-slate-950/70 text-slate-300'
              : 'border border-slate-200 bg-white/90 text-slate-500',
          ].join(' ')}
        >
          {sample.tag}
        </div>
      </div>

      <div className="absolute inset-x-0 bottom-0 z-10 bg-gradient-to-t from-black/80 via-black/30 to-transparent px-4 pb-4 pt-20">
        <div className="text-base font-semibold text-white">{sample.title}</div>
        <div className="mt-1 max-w-[18rem] text-sm text-slate-300">{sample.subtitle}</div>
      </div>

      <video
        className="h-full w-full bg-black object-cover transition duration-500 group-hover:scale-[1.02]"
        autoPlay
        muted
        loop
        playsInline
        preload="metadata"
        poster={sample.poster}
      >
        <source src={sample.src} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
    </article>
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

function LightSectionIntro({ eyebrow, title, body }: { eyebrow: string; title: string; body: string }) {
  return (
    <div className="mx-auto max-w-3xl text-center">
      <div className="inline-flex items-center rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium uppercase tracking-[0.24em] text-slate-500 shadow-sm">
        {eyebrow}
      </div>
      <h2 className="mt-5 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl lg:text-5xl">{title}</h2>
      <p className="mt-4 text-base leading-8 text-slate-600 sm:text-lg">{body}</p>
    </div>
  )
}

function LandingPage() {
  const heroMosaic = [
    getSample('jack-tall-owl'),
    getSample('atlas-daily-action-v2'),
    getSample('tall-owl-plain-ad'),
    getSample('luma-one-shot'),
    getSample('gurunanda-monk'),
  ]

  const showcaseSamples = [
    getSample('product-brand-sample'),
    getSample('arc-two-shot-micro-ad'),
    getSample('atlas-daily-one-shot'),
    getSample('gurunanda-monk-spec'),
    getSample('luma-action-v2'),
    getSample('arc-one-shot'),
  ]

  return (
    <main>
      <section className="relative overflow-hidden">
        <div className="mx-auto max-w-7xl px-6 pb-36 pt-10 sm:px-8 sm:pb-40 lg:px-10 lg:pt-16">
          <div className="grid gap-12 lg:grid-cols-[0.92fr_1.08fr] lg:items-center">
            <div className="relative z-10 max-w-2xl">
              <div className="inline-flex items-center rounded-full border border-white/12 bg-white/5 px-4 py-2 text-xs font-medium uppercase tracking-[0.26em] text-slate-200">
                Premium short-form creative
              </div>

              <h1 className="mt-7 text-5xl font-semibold tracking-tight text-white sm:text-6xl lg:text-7xl">
                Make the product
                <span className="bg-gradient-to-r from-white via-violet-200 to-blue-300 bg-clip-text text-transparent">
                  {' '}feel expensive
                </span>{' '}
                before the caption.
              </h1>

              <p className="mt-6 max-w-xl text-lg leading-8 text-slate-300 sm:text-xl">
                Short-form ads and product reels for brands that need the product to sell fast.
              </p>

              <div className="mt-9 flex flex-col gap-4 sm:flex-row sm:items-center">
                <PrimaryButton href={BOOK_CALL_LINK}>Book a call</PrimaryButton>
                <SecondaryButton href="/brands">View work</SecondaryButton>
              </div>

              <div className="mt-10 grid max-w-2xl gap-4 sm:grid-cols-3">
                {[
                  ['Product-first', 'Clean visuals built around the product.'],
                  ['Testable concepts', 'Reels, one-shots, and campaign directions.'],
                  ['Samples first', 'Judge the work before bigger scope.'],
                ].map(([title, body]) => (
                  <div key={title} className="rounded-[24px] border border-white/10 bg-white/[0.04] p-4 backdrop-blur-xl">
                    <div className="text-sm font-semibold text-white">{title}</div>
                    <p className="mt-2 text-sm leading-6 text-slate-400">{body}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="relative lg:pl-6">
              <div className="pointer-events-none absolute -inset-6 rounded-[40px] bg-[radial-gradient(circle_at_top,rgba(99,102,241,0.26),transparent_36%),radial-gradient(circle_at_bottom_right,rgba(34,197,94,0.18),transparent_34%)] blur-3xl" />
              <div className="relative grid auto-rows-[150px] gap-4 sm:auto-rows-[190px] lg:grid-cols-12 lg:auto-rows-[140px]">
                <AutoVideo sample={heroMosaic[0]} className="lg:col-span-5 lg:row-span-3" />
                <AutoVideo sample={heroMosaic[1]} className="lg:col-span-3 lg:row-span-2" />
                <AutoVideo sample={heroMosaic[2]} className="lg:col-span-4 lg:row-span-3" />
                <AutoVideo sample={heroMosaic[3]} className="lg:col-span-3 lg:row-span-2" />
                <AutoVideo sample={heroMosaic[4]} className="lg:col-span-4 lg:row-span-2" />
              </div>
            </div>
          </div>
        </div>

        <div className="pointer-events-none absolute inset-x-0 bottom-0 h-36 overflow-hidden sm:h-40">
          <div className="absolute inset-x-[-12%] bottom-[-92px] h-52 rounded-[100%] bg-white sm:bottom-[-86px] sm:h-56" />
        </div>
      </section>

      <section id="work" className="relative bg-white text-slate-950">
        <div className="mx-auto max-w-7xl px-6 pb-20 pt-8 sm:px-8 sm:pb-24 lg:px-10 lg:pt-10">
          <LightSectionIntro
            eyebrow="Selected work"
            title="Samples you can judge fast."
            body="Product reels, micro-ads, and character concepts."
          />

          <div className="mt-12 grid auto-rows-[220px] gap-5 md:auto-rows-[250px] lg:grid-cols-12 lg:auto-rows-[170px]">
            <AutoVideo sample={showcaseSamples[0]} tone="light" className="lg:col-span-5 lg:row-span-3" />
            <AutoVideo sample={showcaseSamples[1]} tone="light" className="lg:col-span-4 lg:row-span-2" />
            <AutoVideo sample={showcaseSamples[2]} tone="light" className="lg:col-span-3 lg:row-span-2" />
            <AutoVideo sample={showcaseSamples[3]} tone="light" className="lg:col-span-3 lg:row-span-2" />
            <AutoVideo sample={showcaseSamples[4]} tone="light" className="lg:col-span-4 lg:row-span-2" />
            <AutoVideo sample={showcaseSamples[5]} tone="light" className="lg:col-span-5 lg:row-span-2" />
          </div>

          <div className="mt-10 grid gap-3 rounded-[28px] border border-slate-200 bg-slate-50 p-4 sm:grid-cols-2 xl:grid-cols-4 xl:gap-4 xl:p-5">
            {[
              'Product reels',
              'Micro-ads',
              'Character concepts',
              'Samples before scope',
            ].map((item) => (
              <div key={item} className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm leading-6 text-slate-600 shadow-sm">
                {item}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="capabilities" className="bg-white text-slate-950">
        <div className="mx-auto grid max-w-7xl gap-16 px-6 py-24 sm:px-8 lg:grid-cols-[0.9fr_1.1fr] lg:px-10">
          <div>
            <div className="text-xs font-medium uppercase tracking-[0.26em] text-slate-500">What Clarynt does</div>
            <h2 className="mt-5 text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">
              A tighter first creative test.
            </h2>
            <p className="mt-5 max-w-lg text-lg leading-8 text-slate-600">
              Cleaner visuals, sharper hooks, less fluff.
            </p>
          </div>

          <div className="space-y-8">
            {[
              {
                title: 'Product-first direction',
                body: 'Start with the product and the visual lane.',
              },
              {
                title: 'Multiple angles',
                body: 'Test reels, one-shots, or character concepts.',
              },
              {
                title: 'Direct fit check',
                body: 'Talk with Logan about the first test and scope.',
              },
            ].map((item, index) => (
              <div key={item.title} className="grid gap-4 border-b border-slate-200 pb-8 last:border-b-0 last:pb-0 sm:grid-cols-[72px_1fr] sm:gap-6">
                <div className="text-3xl font-semibold tracking-tight text-slate-300">0{index + 1}</div>
                <div>
                  <div className="text-2xl font-semibold tracking-tight text-slate-950">{item.title}</div>
                  <p className="mt-3 max-w-2xl text-base leading-8 text-slate-600">{item.body}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="process" className="bg-white text-slate-950">
        <div className="mx-auto max-w-7xl px-6 py-24 sm:px-8 lg:px-10">
          <div className="grid gap-12 lg:grid-cols-[0.78fr_1.22fr] lg:items-start">
            <div>
              <div className="text-xs font-medium uppercase tracking-[0.26em] text-slate-500">Process</div>
              <h2 className="mt-5 text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">
                Simple process.
              </h2>
            </div>

            <div className="grid gap-6 md:grid-cols-3">
              {[
                {
                  step: '01',
                  title: 'Choose the first lane',
                  body: 'Pick the first direction to test.',
                },
                {
                  step: '02',
                  title: 'Make the first cut',
                  body: 'Build it around the product.',
                },
                {
                  step: '03',
                  title: 'Refine what works',
                  body: 'Keep the strongest lane and expand from there.',
                },
              ].map((item) => (
                <div key={item.step} className="rounded-[30px] border border-slate-200 bg-slate-50 p-6">
                  <div className="text-sm font-medium text-slate-400">{item.step}</div>
                  <div className="mt-4 text-2xl font-semibold tracking-tight text-slate-950">{item.title}</div>
                  <p className="mt-3 text-sm leading-7 text-slate-600">{item.body}</p>
                </div>
              ))}
            </div>
          </div>

          <div id="contact" className="mt-16 rounded-[36px] border border-slate-200 bg-slate-950 px-6 py-8 text-white shadow-[0_30px_80px_rgba(15,23,42,0.16)] sm:px-8 lg:flex lg:items-center lg:justify-between lg:gap-8">
            <div>
              <div className="text-2xl font-semibold tracking-tight text-white">Book a call for the first creative test.</div>
              <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-300">
                Send Logan the product and category. He’ll tell you if the fit is real and what to test first.
              </p>
              <div className="mt-4 flex flex-wrap gap-3 text-sm text-slate-300">
                <a href={PHONE_LINK} className="rounded-full border border-white/10 bg-white/5 px-4 py-2 transition hover:border-white/20 hover:bg-white/10">
                  {PHONE_DISPLAY}
                </a>
                <a href={EMAIL_LINK} className="rounded-full border border-white/10 bg-white/5 px-4 py-2 transition hover:border-white/20 hover:bg-white/10">
                  {EMAIL}
                </a>
              </div>
            </div>
            <div className="mt-6 flex flex-col gap-4 sm:flex-row lg:mt-0">
              <PrimaryButton href={BOOK_CALL_LINK}>Book a call</PrimaryButton>
              <SecondaryButton href={EMAIL_LINK}>Email Logan</SecondaryButton>
            </div>
          </div>
        </div>
      </section>

      <footer className="border-t border-slate-200 bg-white text-slate-950">
        <div className="mx-auto grid max-w-7xl gap-10 px-6 py-16 sm:px-8 lg:grid-cols-[1.15fr_0.85fr_0.85fr_0.85fr] lg:px-10">
          <div>
            <Logo tone="light" />
            <p className="mt-5 max-w-sm text-sm leading-7 text-slate-600">
              Premium short-form creative for brands that need a stronger first impression.
            </p>
          </div>

          <div>
            <div className="text-sm font-semibold text-slate-950">Work</div>
            <div className="mt-4 space-y-3 text-sm text-slate-600">
              <a href="/brands" className="block transition hover:text-slate-950">
                Sample library
              </a>
              <a href="/#work" className="block transition hover:text-slate-950">
                Selected work
              </a>
              <a href="/dental" className="block transition hover:text-slate-950">
                Dental sample
              </a>
            </div>
          </div>

          <div>
            <div className="text-sm font-semibold text-slate-950">Sections</div>
            <div className="mt-4 space-y-3 text-sm text-slate-600">
              <a href="/#capabilities" className="block transition hover:text-slate-950">
                Capabilities
              </a>
              <a href="/#process" className="block transition hover:text-slate-950">
                Process
              </a>
              <a href="/#work" className="block transition hover:text-slate-950">
                Work
              </a>
            </div>
          </div>

          <div>
            <div className="text-sm font-semibold text-slate-950">Contact</div>
            <div className="mt-4 space-y-3 text-sm text-slate-600">
              <a href={EMAIL_LINK} className="block transition hover:text-slate-950">
                {EMAIL}
              </a>
              <a href={PHONE_LINK} className="block transition hover:text-slate-950">
                {PHONE_DISPLAY}
              </a>
            </div>
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
            Browse the current Clarynt product-brand sample library: product reels, one-shots, micro-ads, and character-led concepts.
          </p>

          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            {[
              {
                title: 'Product reels',
                body: 'Premium product-focused creative for paid social, landing pages, and brand proof.',
              },
              {
                title: 'One-shots and micro-ads',
                body: 'Shorter concept lanes for testing and tighter campaign pages.',
              },
              {
                title: 'Character and spec work',
                body: 'Stronger concept directions when the brand needs more identity and memorability.',
              },
            ].map((item) => (
              <div key={item.title} className="rounded-3xl border border-white/10 bg-white/5 p-4 backdrop-blur">
                <div className="text-sm font-semibold text-white">{item.title}</div>
                <p className="mt-2 text-sm leading-6 text-slate-400">{item.body}</p>
              </div>
            ))}
          </div>

          <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center">
            <PrimaryButton href={BOOK_CALL_LINK}>Book a call</PrimaryButton>
            <SecondaryButton href="#featured-sample">Watch featured sample</SecondaryButton>
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
            <div className="text-sm text-slate-400">Current product-brand samples available to review.</div>
          </div>
          <div className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-400">
            Current samples
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2 xl:grid-cols-3">
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
            A focused sample for practices that want patient-facing education before broader ad creative.
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
            <PrimaryButton href={BOOK_CALL_LINK}>Book a call</PrimaryButton>
            <SecondaryButton href={EMAIL_LINK}>Email Logan</SecondaryButton>
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
        title: 'Clarynt | Product Brand Reels',
        description:
          'Premium short-form product ads and sample reels for brands that want cleaner visuals, stronger hooks, and a higher-trust first impression.',
      }
    }

    if (isDental) {
      return {
        title: 'Clarynt | Dental Sample',
        description:
          'Patient-education videos that help dental offices build trust with potential patients online.',
      }
    }

    return {
      title: 'Clarynt | Premium Short-Form Creative',
      description:
        'Clarynt creates premium short-form ads and product reels for brands that want cleaner visuals, stronger hooks, and proof-first creative.',
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
