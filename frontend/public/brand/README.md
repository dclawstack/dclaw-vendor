# DClaw Vendor — Brand Assets

The DClaw Vendor mark is a **clasped handshake** (supplier deals & POs) — rendered in white inside the brand's purple rounded square (`#7660A8`, 14-unit corner radius). It is a sibling of the other DClaw apps' marks — all share the purple-square shell so they read as one suite, while the inner glyph differentiates the product. (This replaces the earlier placeholder, which had reused dclaw-marketing's broadcast glyph.)

The handshake glyph is adapted from the **lucide** "handshake" icon (https://lucide.dev), used under the **ISC License** — the same icon family the DClaw app UIs already use.

## Files

### SVG masters (`logos/`)

| File | ViewBox | Use |
|---|---|---|
| `dclaw-icon-purple.svg` | 64×64 | App icon, favicon, marks on light surfaces |
| `dclaw-icon-white.svg` | 64×64 | Inverted (white square, purple glyph) for dark surfaces |
| `dclaw-logo-purple.svg` | 296×64 | Wordmark for light surfaces — "DClaw" (ink) + "Vendor" (purple) |
| `dclaw-logo-white.svg` | 296×64 | Wordmark for dark surfaces — "DClaw" (white) + "Vendor" (light purple) |

### Icon rasters (`logos/dclaw-icon-{purple,white}-{size}.{png,webp}`)

Sizes: **16, 32, 48, 64, 96, 128, 180, 192, 256, 512, 1024** — 11 sizes × 2 colors × 2 formats = **44 files**.

### Wordmark rasters (`logos/dclaw-logo-{purple,white}-h{height}.{png,webp}`)

Heights: **32, 48, 64, 96, 128, 192, 256** — 7 heights × 2 colors × 2 formats = **28 files**. Width is `height × 296/64`.

### Favicons (mirrored to `/frontend/public/` root and `/landing/public/` root)

`favicon.svg`, `favicon.png`, `favicon-{16,32,48}x{16,32,48}.{png,webp}`, `apple-touch-icon.{png,webp}` (180×180), `android-chrome-{192,512}x{192,512}.{png,webp}`, `site.webmanifest`.

## Format selection rule

- **SVG** for any surface that can serve vectors — never blurs, scales perfectly.
- **WebP** for fast-loading raster surfaces (~50–70% smaller than PNG).
- **PNG** as the universal fallback (legacy email clients, some social cards).

## Color tokens

- Primary purple: `#7660A8`
- Secondary purple (wordmark on dark): `#C9C0DE`
- Ink (wordmark on light): `#0F0F12`
- White: `#FFFFFF`
