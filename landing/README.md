# DClaw Vendor — Landing

Standalone marketing landing page for DClaw Vendor. Built with **Next.js 15 + React 19
+ Tailwind CSS v4** and the DKube brand (purple `--dk-*` tokens, Poppins), mirroring the
dclaw-sales / dclaw-marketing landing apps.

Single page: NavBar · Hero · Logo strip · Features · Lifecycle · How it works ·
Analytics · Deploy · CTA · Footer.

## Run

```bash
npm install
npm run dev        # http://localhost:3000
```

The hero / nav / CTA "Launch the app" buttons point at `NEXT_PUBLIC_APP_URL`
(defaults to the running app at `http://localhost:3019`):

```bash
NEXT_PUBLIC_APP_URL=http://localhost:3019 npm run build
```

## Deploy

Live at **https://dclaw-vendor.vercel.app** (Vercel project `dclaw-vendor`, root dir
`landing/`). Redeploy from this directory:

```bash
vercel deploy --prod --yes --scope deepro-mallick-s-projects
```
