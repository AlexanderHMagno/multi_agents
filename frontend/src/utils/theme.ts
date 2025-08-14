// MarketMinds AI Theme Configuration
export interface MarketMindsTheme {
  primary: {
    main: string;
    hover: string;
    light: string;
    background: string;
  };
  secondary: {
    main: string;
    hover: string;
    light: string;
    background: string;
  };
  neutral: {
    50: string;
    100: string;
    200: string;
    300: string;
    400: string;
    500: string;
    600: string;
    700: string;
    800: string;
    900: string;
  };
  status: {
    success: string;
    warning: string;
    error: string;
    info: string;
  };
}

// Default MarketMinds AI Theme
export const defaultTheme: MarketMindsTheme = {
  primary: {
    main: '#EA580C', // orange-600
    hover: '#C2410C', // orange-700
    light: '#FED7AA', // orange-200
    background: '#FFF7ED', // orange-50
  },
  secondary: {
    main: '#1D4ED8', // blue-700
    hover: '#1E40AF', // blue-800
    light: '#BFDBFE', // blue-200
    background: '#EFF6FF', // blue-50
  },
  neutral: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
  },
  status: {
    success: '#059669', // green-600
    warning: '#D97706', // amber-600
    error: '#DC2626', // red-600
    info: '#0891B2', // cyan-600
  },
};

// Alternative Theme Options
export const themeOptions = {
  // Corporate Theme
  corporate: {
    ...defaultTheme,
    primary: {
      main: '#1F2937', // gray-800
      hover: '#111827', // gray-900
      light: '#D1D5DB', // gray-300
      background: '#F9FAFB', // gray-50
    },
    secondary: {
      main: '#3B82F6', // blue-500
      hover: '#2563EB', // blue-600
      light: '#DBEAFE', // blue-100
      background: '#EFF6FF', // blue-50
    },
  },
  
  // Modern Theme
  modern: {
    ...defaultTheme,
    primary: {
      main: '#7C3AED', // violet-600
      hover: '#6D28D9', // violet-700
      light: '#DDD6FE', // violet-200
      background: '#F5F3FF', // violet-50
    },
    secondary: {
      main: '#10B981', // emerald-500
      hover: '#059669', // emerald-600
      light: '#D1FAE5', // emerald-100
      background: '#ECFDF5', // emerald-50
    },
  },
  
  // Warm Theme
  warm: {
    ...defaultTheme,
    primary: {
      main: '#DC2626', // red-600
      hover: '#B91C1C', // red-700
      light: '#FECACA', // red-200
      background: '#FEF2F2', // red-50
    },
    secondary: {
      main: '#F59E0B', // amber-500
      hover: '#D97706', // amber-600
      light: '#FED7AA', // amber-200
      background: '#FFFBEB', // amber-50
    },
  },
};

// Function to apply theme to CSS variables
export const applyTheme = (theme: MarketMindsTheme) => {
  const root = document.documentElement;
  
  // Apply primary colors
  root.style.setProperty('--mm-primary', theme.primary.main);
  root.style.setProperty('--mm-primary-hover', theme.primary.hover);
  root.style.setProperty('--mm-primary-light', theme.primary.light);
  root.style.setProperty('--mm-primary-bg', theme.primary.background);
  
  // Apply secondary colors
  root.style.setProperty('--mm-secondary', theme.secondary.main);
  root.style.setProperty('--mm-secondary-hover', theme.secondary.hover);
  root.style.setProperty('--mm-secondary-light', theme.secondary.light);
  root.style.setProperty('--mm-secondary-bg', theme.secondary.background);
  
  // Apply neutral colors
  root.style.setProperty('--mm-gray-50', theme.neutral[50]);
  root.style.setProperty('--mm-gray-100', theme.neutral[100]);
  root.style.setProperty('--mm-gray-200', theme.neutral[200]);
  root.style.setProperty('--mm-gray-300', theme.neutral[300]);
  root.style.setProperty('--mm-gray-400', theme.neutral[400]);
  root.style.setProperty('--mm-gray-500', theme.neutral[500]);
  root.style.setProperty('--mm-gray-600', theme.neutral[600]);
  root.style.setProperty('--mm-gray-700', theme.neutral[700]);
  root.style.setProperty('--mm-gray-800', theme.neutral[800]);
  root.style.setProperty('--mm-gray-900', theme.neutral[900]);
  
  // Apply status colors
  root.style.setProperty('--mm-success', theme.status.success);
  root.style.setProperty('--mm-warning', theme.status.warning);
  root.style.setProperty('--mm-error', theme.status.error);
  root.style.setProperty('--mm-info', theme.status.info);
};

// Function to get current theme from CSS variables
export const getCurrentTheme = (): MarketMindsTheme => {
  const root = document.documentElement;
  
  return {
    primary: {
      main: getComputedStyle(root).getPropertyValue('--mm-primary').trim(),
      hover: getComputedStyle(root).getPropertyValue('--mm-primary-hover').trim(),
      light: getComputedStyle(root).getPropertyValue('--mm-primary-light').trim(),
      background: getComputedStyle(root).getPropertyValue('--mm-primary-bg').trim(),
    },
    secondary: {
      main: getComputedStyle(root).getPropertyValue('--mm-secondary').trim(),
      hover: getComputedStyle(root).getPropertyValue('--mm-secondary-hover').trim(),
      light: getComputedStyle(root).getPropertyValue('--mm-secondary-light').trim(),
      background: getComputedStyle(root).getPropertyValue('--mm-secondary-bg').trim(),
    },
    neutral: {
      50: getComputedStyle(root).getPropertyValue('--mm-gray-50').trim(),
      100: getComputedStyle(root).getPropertyValue('--mm-gray-100').trim(),
      200: getComputedStyle(root).getPropertyValue('--mm-gray-200').trim(),
      300: getComputedStyle(root).getPropertyValue('--mm-gray-300').trim(),
      400: getComputedStyle(root).getPropertyValue('--mm-gray-400').trim(),
      500: getComputedStyle(root).getPropertyValue('--mm-gray-500').trim(),
      600: getComputedStyle(root).getPropertyValue('--mm-gray-600').trim(),
      700: getComputedStyle(root).getPropertyValue('--mm-gray-700').trim(),
      800: getComputedStyle(root).getPropertyValue('--mm-gray-800').trim(),
      900: getComputedStyle(root).getPropertyValue('--mm-gray-900').trim(),
    },
    status: {
      success: getComputedStyle(root).getPropertyValue('--mm-success').trim(),
      warning: getComputedStyle(root).getPropertyValue('--mm-warning').trim(),
      error: getComputedStyle(root).getPropertyValue('--mm-error').trim(),
      info: getComputedStyle(root).getPropertyValue('--mm-info').trim(),
    },
  };
}; 