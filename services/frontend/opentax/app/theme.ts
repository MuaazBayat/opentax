import { createTheme, PaletteMode } from '@mui/material/styles';

export const getTheme = (mode: PaletteMode) => createTheme({
  palette: {
    mode,
    primary: {
      main: '#6366f1', // Indigo
      light: '#818cf8',
      dark: '#4f46e5',
    },
    secondary: {
      main: '#14b8a6', // Teal
      light: '#2dd4bf',
      dark: '#0d9488',
    },
    ...(mode === 'dark' ? {
      background: {
        default: '#0f172a', // Slate 900
        paper: '#1e293b', // Slate 800
      },
      text: {
        primary: '#f1f5f9', // Slate 100
        secondary: '#cbd5e1', // Slate 300
      },
    } : {
      background: {
        default: '#f8fafc', // Slate 50
        paper: '#ffffff', // White
      },
      text: {
        primary: '#0f172a', // Slate 900
        secondary: '#475569', // Slate 600
      },
    }),
    success: {
      main: '#10b981', // Emerald
    },
    error: {
      main: '#ef4444', // Red
    },
    warning: {
      main: '#f59e0b', // Amber
    },
    info: {
      main: '#3b82f6', // Blue
    },
  },
  typography: {
    fontFamily: 'var(--font-geist-sans)',
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
  },
});
