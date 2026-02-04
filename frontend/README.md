# Frontend - Todo Application

Next.js 14 frontend with authentication and user isolation.

## Features

- User signup and signin
- JWT token management
- Protected routes
- Automatic token refresh
- Responsive design with Tailwind CSS
- TypeScript support

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env.local
# Edit .env.local with your backend API URL
```

3. Start development server:
```bash
npm run dev
```

The app will be available at http://localhost:3000

## Pages

- `/` - Landing page (redirects to /signin or /tasks)
- `/signin` - User signin page
- `/signup` - User signup page
- `/tasks` - Protected tasks page (requires authentication)

## Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://localhost:8000)
- `BETTER_AUTH_SECRET` - Secret key matching backend (for Better Auth)

## Authentication Flow

1. User signs up or signs in
2. JWT token received from backend
3. Token stored in localStorage
4. Token automatically attached to API requests via Axios interceptor
5. Protected routes check authentication status
6. Expired/invalid tokens trigger automatic logout and redirect to signin

## Development

```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

## Project Structure

```
frontend/
├── app/
│   ├── (auth)/
│   │   ├── signin/
│   │   └── signup/
│   ├── (app)/
│   │   └── tasks/
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/
│   └── ProtectedRoute.tsx
├── contexts/
│   └── AuthContext.tsx
├── lib/
│   └── api-client.ts
└── hooks/
```

## Security Features

- Client-side password validation
- Automatic token expiration handling
- Protected route guards
- Secure token storage
- HTTPS recommended for production
