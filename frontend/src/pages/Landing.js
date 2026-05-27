import React, { Component } from 'react';
import LandingDesktop from './desktop/Landing';
import LandingMobile from './mobile/Landing';

class Landing extends Component {
  state = {
    isMobile: window.innerWidth <= 768,
  };

  updateIsMobile = () => {
    const isMobile = window.innerWidth <= 768;
    if (this.state.isMobile !== isMobile) {
      this.setState({ isMobile });
    }
  };

  componentDidMount() {
    // Debounce the resize event to prevent excessive updates
    let resizeTimeout;
    const debouncedResize = () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(this.updateIsMobile, 100);
    };
    
    window.addEventListener('resize', debouncedResize);
    this.cleanup = () => {
      window.removeEventListener('resize', debouncedResize);
      clearTimeout(resizeTimeout);
    };
  }

  componentWillUnmount() {
    if (this.cleanup) {
      this.cleanup();
    }
  }

  render() {
    const { isMobile } = this.state;
    return isMobile ? <LandingMobile /> : <LandingDesktop />;
  }
}

export default Landing;
