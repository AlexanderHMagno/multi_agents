import { useState, useEffect } from 'react';
import { applyTheme, getCurrentTheme, themeOptions, defaultTheme, MarketMindsTheme } from '../utils/theme';

export const ThemeSwitcher = () => {
  const [currentTheme, setCurrentTheme] = useState<MarketMindsTheme>(defaultTheme);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    // Get current theme from CSS variables on mount
    const theme = getCurrentTheme();
    setCurrentTheme(theme);
  }, []);

  const handleThemeChange = (themeName: string) => {
    let newTheme: MarketMindsTheme;
    
    switch (themeName) {
      case 'corporate':
        newTheme = themeOptions.corporate;
        break;
      case 'modern':
        newTheme = themeOptions.modern;
        break;
      case 'warm':
        newTheme = themeOptions.warm;
        break;
      default:
        newTheme = defaultTheme;
    }
    
    applyTheme(newTheme);
    setCurrentTheme(newTheme);
    setIsOpen(false);
    
    // Save theme preference to localStorage
    localStorage.setItem('marketminds-theme', themeName);
  };

  const getThemePreview = (theme: MarketMindsTheme) => (
    <div className="flex items-center gap-2">
      <div className="flex gap-1">
        <div 
          className="w-3 h-3 rounded-full" 
          style={{ backgroundColor: theme.primary.main }}
        />
        <div 
          className="w-3 h-3 rounded-full" 
          style={{ backgroundColor: theme.secondary.main }}
        />
      </div>
      <span className="capitalize">{theme === defaultTheme ? 'default' : Object.keys(themeOptions).find(key => themeOptions[key as keyof typeof themeOptions] === theme)}</span>
    </div>
  );

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="btn btn-ghost btn-circle"
        title="Switch Theme"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zM21 5a2 2 0 00-2-2h-1a2 2 0 00-2 2v1a2 2 0 002 2h1a2 2 0 002-2V5zM21 12a2 2 0 00-2 2v1a2 2 0 002 2h1a2 2 0 002-2v-1a2 2 0 00-2-2zM21 19a2 2 0 00-2 2v1a2 2 0 002 2h1a2 2 0 002-2v-1a2 2 0 00-2-2z" />
        </svg>
      </button>
      
      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-xl border border-gray-200 z-50">
          <div className="p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">MarketMinds AI Themes</h3>
            
            <div className="space-y-3">
              {/* Default Theme */}
              <button
                onClick={() => handleThemeChange('default')}
                className={`w-full text-left p-3 rounded-lg border transition-colors ${
                  currentTheme === defaultTheme 
                    ? 'border-mm-primary bg-mm-primary-bg' 
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                {getThemePreview(defaultTheme)}
              </button>
              
              {/* Corporate Theme */}
              <button
                onClick={() => handleThemeChange('corporate')}
                className={`w-full text-left p-3 rounded-lg border transition-colors ${
                  currentTheme === themeOptions.corporate 
                    ? 'border-mm-primary bg-mm-primary-bg' 
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                {getThemePreview(themeOptions.corporate)}
              </button>
              
              {/* Modern Theme */}
              <button
                onClick={() => handleThemeChange('modern')}
                className={`w-full text-left p-3 rounded-lg border transition-colors ${
                  currentTheme === themeOptions.modern 
                    ? 'border-mm-primary bg-mm-primary-bg' 
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                {getThemePreview(themeOptions.modern)}
              </button>
              
              {/* Warm Theme */}
              <button
                onClick={() => handleThemeChange('warm')}
                className={`w-full text-left p-3 rounded-lg border transition-colors ${
                  currentTheme === themeOptions.warm 
                    ? 'border-mm-primary bg-mm-primary-bg' 
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                {getThemePreview(themeOptions.warm)}
              </button>
            </div>
            
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-600">
                Current: <span className="font-medium text-mm-primary">{getThemePreview(currentTheme).props.children[1].props.children}</span>
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}; 