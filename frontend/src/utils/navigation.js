// Navigation utility to prevent throttling
let navigationTimeout = null;

export const debouncedNavigate = (navigate, to, options = {}) => {
  // Clear any existing timeout
  if (navigationTimeout) {
    clearTimeout(navigationTimeout);
  }
  
  // Set a new timeout for navigation
  navigationTimeout = setTimeout(() => {
    navigate(to, options);
  }, 100); // 100ms debounce
};

export const clearNavigationTimeout = () => {
  if (navigationTimeout) {
    clearTimeout(navigationTimeout);
    navigationTimeout = null;
  }
}; 