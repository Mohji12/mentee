// Debug utility for monitoring React performance and errors

// Monitor for excessive re-renders
let renderCounts = new Map();

export const monitorRenders = (componentName) => {
  const count = renderCounts.get(componentName) || 0;
  renderCounts.set(componentName, count + 1);
  
  // Log if component renders too frequently
  if (count > 50) {
    console.warn(`Component ${componentName} has rendered ${count} times. Consider optimizing.`);
  }
};

// Monitor for memory leaks
export const monitorMemory = () => {
  if (performance.memory) {
    const memory = performance.memory;
    const usedMB = Math.round(memory.usedJSHeapSize / 1048576);
    const totalMB = Math.round(memory.totalJSHeapSize / 1048576);
    
    if (usedMB > 100) { // Warning if using more than 100MB
      console.warn(`High memory usage: ${usedMB}MB / ${totalMB}MB`);
    }
  }
};

// Monitor for navigation throttling
let navigationCount = 0;
let lastNavigationTime = 0;

export const monitorNavigation = () => {
  const now = Date.now();
  navigationCount++;
  
  if (now - lastNavigationTime < 100) { // Less than 100ms between navigations
    console.warn('Navigation throttling detected. Consider debouncing navigation calls.');
  }
  
  lastNavigationTime = now;
  
  // Reset counter every 10 seconds
  setTimeout(() => {
    navigationCount = 0;
  }, 10000);
};

// Global error handler
export const setupGlobalErrorHandling = () => {
  window.addEventListener('error', (event) => {
    console.error('Global error caught:', event.error);
  });
  
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
  });
};

// Performance monitoring (dev only — thresholds tuned for SPA: full navigations are often 300–800ms)
const SLOW_MEASURE_MS = 100;
const SLOW_NAVIGATION_MS = 2500;

export const monitorPerformance = () => {
  if ('performance' in window && typeof PerformanceObserver !== 'undefined') {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        const isNavigation = entry.entryType === 'navigation';
        const threshold = isNavigation ? SLOW_NAVIGATION_MS : SLOW_MEASURE_MS;
        if (entry.duration > threshold) {
          console.warn(
            `Slow operation detected (${entry.entryType}): ${entry.name} took ${entry.duration.toFixed(0)}ms`
          );
        }
      }
    });

    observer.observe({ entryTypes: ['measure', 'navigation'] });
  }
};

// Initialize all monitoring
export const initializeDebugging = () => {
  if (import.meta.env.DEV) {
    setupGlobalErrorHandling();
    monitorPerformance();
    
    // Monitor memory usage periodically
    setInterval(monitorMemory, 30000); // Every 30 seconds
  }
}; 