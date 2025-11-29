# OpenTax Frontend

Next.js frontend for OpenTax.

## Prerequisites

- Node.js 20+
- npm

## Setup

### 1. Install dependencies

```bash
npm install
```

### 2. Environment configuration

Create a `.env.local` file:

```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## Development

### Run the dev server

```bash
npm run dev
```

The app will be available at `http://localhost:3000`.

### Build for production

```bash
npm run build
```

### Start production server

```bash
npm start
```

### Lint

```bash
npm run lint
```

## Tech Stack

- Next.js 16
- React 19
- TypeScript
- MUI (Material UI)
- Tailwind CSS
- Zustand (state management)