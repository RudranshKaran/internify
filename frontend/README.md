# Internify Frontend

This is the frontend application for Internify, built with Next.js 14, TypeScript, and Tailwind CSS.

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Components:** Custom components + shadcn/ui style
- **Authentication:** Supabase Auth
- **HTTP Client:** Axios
- **Animations:** Framer Motion
- **Icons:** Lucide React

## Getting Started

### Prerequisites

- Node.js 18 or higher
- npm or yarn

### Installation

```bash
npm install
# or
yarn install
```

### Environment Variables

Create a `.env.local` file in the root directory:

```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### Development

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

### Build

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/                    # Next.js 14 App Router
│   ├── page.tsx           # Landing page
│   ├── login/             # Authentication
│   ├── dashboard/         # Main dashboard
│   ├── email-preview/     # Email generation & preview
│   ├── history/           # Email history
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── components/            # Reusable components
│   ├── Navbar.tsx
│   ├── JobCard.tsx
│   ├── ResumeUploader.tsx
│   ├── EmailPreview.tsx
│   ├── Loader.tsx
│   └── Toast.tsx
├── lib/                   # Utilities
│   ├── supabaseClient.ts  # Supabase config
│   ├── api.ts             # API client
│   └── utils.ts           # Helper functions
└── public/                # Static assets
```

## Features

- 🔐 Secure authentication with Supabase
- 📄 PDF resume upload and parsing
- 🔍 Real-time job search
- 🤖 AI-powered email generation
- ✉️ One-click email sending
- 📊 Application tracking dashboard
- 🎨 Beautiful, responsive UI
- ⚡ Fast page loads with Next.js

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import repository in Vercel
3. Set environment variables
4. Deploy!

Vercel will automatically detect Next.js and configure everything.

### Environment Variables for Production

```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_BACKEND_URL=https://your-backend.onrender.com
```

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
