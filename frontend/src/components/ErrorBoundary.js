import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Suppress video-related errors from html5-qrcode library
    const errorMsg = String(error?.message || error?.toString() || '');
    
    if (
      errorMsg.includes('onabort') ||
      errorMsg.includes('RenderedCameraImpl') ||
      errorMsg.includes('play() request was interrupted') ||
      errorMsg.includes('new load request') ||
      errorMsg.includes('video surface')
    ) {
      // Don't set error state for these expected errors
      return { hasError: false };
    }
    
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Suppress video-related errors from html5-qrcode library
    const errorMsg = String(error?.message || error?.toString() || '');
    const errorStack = String(errorInfo?.componentStack || '');
    
    if (
      errorMsg.includes('onabort') ||
      errorMsg.includes('RenderedCameraImpl') ||
      errorMsg.includes('play() request was interrupted') ||
      errorMsg.includes('new load request') ||
      errorMsg.includes('video surface') ||
      errorStack.includes('RenderedCameraImpl') ||
      errorStack.includes('onabort')
    ) {
      // Suppress these errors - they're expected from the QR scanner library
      return;
    }
    
    // Log other errors to console
    console.error('Error caught by boundary:', error, errorInfo);
    
    // Update state with error details
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return (
        <div style={{ 
          padding: '20px', 
          textAlign: 'center', 
          fontFamily: 'Arial, sans-serif',
          backgroundColor: '#f8f9fa',
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center'
        }}>
          <h2 style={{ color: '#dc3545', marginBottom: '20px' }}>
            Something went wrong
          </h2>
          <p style={{ color: '#6c757d', marginBottom: '20px' }}>
            We're sorry, but something unexpected happened. Please try refreshing the page.
          </p>
          <button 
            onClick={() => window.location.reload()} 
            style={{
              padding: '10px 20px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            Refresh Page
          </button>
          {import.meta.env.DEV && this.state.error && (
            <details style={{ marginTop: '20px', textAlign: 'left', maxWidth: '600px' }}>
              <summary style={{ cursor: 'pointer', color: '#007bff' }}>
                Error Details (Development)
              </summary>
              <pre style={{ 
                backgroundColor: '#f8f9fa', 
                padding: '10px', 
                borderRadius: '5px',
                overflow: 'auto',
                fontSize: '12px'
              }}>
                {this.state.error && this.state.error.toString()}
                <br />
                {this.state.errorInfo.componentStack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 