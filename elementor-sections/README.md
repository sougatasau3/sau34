# KolkataElderCare - Elementor Section Templates

These JSON files are WordPress Elementor-compatible section templates designed for the **Hello Elementor** theme. Each file represents a distinct section of the KolkataElderCare landing page.

## Prerequisites

- WordPress 6.x+
- Elementor Pro (recommended) or Elementor Free
- Hello Elementor theme (activated)
- Google Fonts: **Fraunces** (serif) and **Jost** (sans-serif)

## Section Files

| # | File | Section |
|---|------|---------|
| 01 | `01-top-strip.json` | Top info strip with phone numbers and WhatsApp CTA |
| 02 | `02-navigation.json` | Sticky navigation bar with logo, menu, and CTAs |
| 03 | `03-hero.json` | Hero section with headline, CTAs, trust badges, stats |
| 04 | `04-about.json` | About/Story section with quote card and differentiators |
| 05 | `05-services.json` | 3-column services grid (Gerontology, Telemedicine, NRI) |
| 06 | `06-how-it-works.json` | 4-step process with WhatsApp chat mockup |
| 07 | `07-pricing.json` | 3-tier pricing cards (Basic, Complete, Dementia) |
| 08 | `08-doctors.json` | 4-column doctors team grid |
| 09 | `09-testimonials.json` | 2x2 testimonial grid with NRI badges |
| 10 | `10-whatsapp-cta.json` | WhatsApp call-to-action section |
| 11 | `11-contact.json` | Contact form + info cards |
| 12 | `12-footer.json` | Footer with brand, links, and disclaimer |

## How to Import

### Method 1: Elementor Template Import
1. In WordPress admin, go to **Templates > Saved Templates**
2. Click **Import Templates**
3. Upload each JSON file one at a time
4. Create a new page, edit with Elementor
5. Insert each template section in order (01 → 12)

### Method 2: Copy-Paste (Elementor Pro)
1. Open the JSON file
2. Copy the content within the `"elements"` array
3. In Elementor editor, right-click > Paste from clipboard

## Responsive Breakpoints

All sections include responsive settings for:
- **Desktop**: Default (1024px+)
- **Tablet**: 768px - 1024px
- **Mobile**: Below 768px

Key responsive behaviors:
- Grid layouts collapse to single column on mobile
- Font sizes scale down proportionally
- Navigation links hide on tablet/mobile (use hamburger menu widget)
- Hero visual column hides on mobile
- Padding reduces on smaller screens

## Color Tokens

| Token | Hex | Usage |
|-------|-----|-------|
| Ink | `#1C1A16` | Primary text |
| Gold | `#C8851A` | Accents, labels |
| Blue | `#1A3D6B` | Featured sections, nav |
| Green | `#1A6B4A` | Check marks, success |
| WhatsApp | `#25D366` | CTA buttons |
| Cream | `#FDFAF5` | Page background |
| Sand | `#F3EDE0` | Alternate section bg |
| Border | `#E0D8C8` | Card borders |
| Muted | `#6B6355` | Secondary text |

## Typography

- **Headings**: Fraunces (Google Fonts) — serif, weight 700/900
- **Body**: Jost (Google Fonts) — sans-serif, weight 300-600

## Notes

- All WhatsApp links point to `+91 72888 18181`
- Forms submit via WhatsApp redirect (JavaScript-based in original)
- For Elementor Pro Form widget, configure email/webhook actions separately
- Replace placeholder images/emojis with actual photos for production
- The navigation section works best with Elementor's built-in Nav Menu widget with a WordPress menu configured
