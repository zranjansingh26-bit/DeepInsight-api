# DeepInsight Starter Suite - Landing Page

Marketing site for DeepInsight Starter Suite, the AI-powered analytics platform documented in the companion `DeepInsight Documentation` folder.

## Stack

- Next.js 14 (App Router) + TypeScript
- Tailwind CSS with custom violet/lavender brand palette
- shadcn-style UI primitives built on Radix
- Framer Motion for scroll reveals and parallax mist
- Fraunces (display) + Inter (body) via `next/font/google`

## Quick start

```bash
npm install
npm run dev
# open http://localhost:3000
```

## Production build

```bash
npm run build
npm run start
```

## Project layout

```
deepinsight-landing/
├── app/
│   ├── layout.tsx       # Root layout, fonts, metadata
│   ├── page.tsx         # Landing page (composes marketing sections)
│   └── globals.css      # Brand tokens, gradient mesh, mist utilities
├── components/
│   ├── ui/              # Button, Badge, Card, Accordion, Tabs primitives
│   └── marketing/       # Section components (nav, hero, pricing, faq, ...)
├── lib/
│   ├── site.ts          # Single source of truth: nav, plans, FAQ, use cases
│   └── utils.ts         # cn() helper
├── tailwind.config.ts   # Brand palette + custom shadows + animations
└── package.json
```

## Editing content

All copy that lives outside the inline section JSX is centralised in `lib/site.ts`:

- Navigation links
- Pricing tiers
- Feature deep-dive items
- Use case tabs (persona / pain / outcome)
- FAQ items
- Footer link columns

Change values there and the site updates everywhere it is referenced.

## Brand tokens

The palette is defined in `tailwind.config.ts` and surfaced as Tailwind colour utilities:

| Token | Hex | Use |
|---|---|---|
| `violet-900` | `#4C1D95` | Deep accents, section openers |
| `violet-700` | `#6D28D9` | Primary buttons, brand emphasis |
| `violet-500` | `#8B5CF6` | Hover states, secondary fills |
| `violet-300` (`lavender`) | `#C4B5FD` | Highlights, dividers |
| `violet-100` (`mist`) | `#EDE9FE` | Soft backgrounds |
| `violet-50` (`cloud`) | `#F5F3FF` | Page-section tinting |
| `ink` | `#1E1B4B` | Headlines |
| `slate-500` | `#3F3C6B` | Body copy |

## License

Internal asset for the DeepInsight pilot. Not for redistribution.
