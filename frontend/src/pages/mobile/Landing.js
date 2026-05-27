import React from 'react';
import { Link } from 'react-router-dom';
import '../../assets/css/Landingmobile.css';
import HeroImage from '../../assets/images/hero.png'; // Add a nice full-width hero
import EfficiencyImage from '../../assets/images/efficiency.png';
import PersonalizationImage from '../../assets/images/personalization.png';
import LearningImage from '../../assets/images/learning.png';
const MENTEE_TRACKER_LOGO_URL = 'https://jgi-menteetrackers.s3.ap-south-1.amazonaws.com/logo_mentee-removebg-preview.png';
const JAIN_LOGO_URL = 'https://jgi-menteetrackers.s3.ap-south-1.amazonaws.com/Jain-Logo.png';
import Chatbot from '../Chatbot';
import Footer from '../components/Footer';

const MobileLandingPage = () => {
  return (
    <div className="mlp-container">
      {/* Header Logos */}
      <div className="mlp-header">
        <Link to="/" className="mlp-logo-left">
          <img src={MENTEE_TRACKER_LOGO_URL} alt="Mentee Tracker" />
        </Link>
        <div className="mlp-logo-right">
          <img src={JAIN_LOGO_URL} alt="Jain University" />
        </div>
      </div>

      {/* Hero Image */}
      <div className="mlp-hero-image">
        <img src={HeroImage} alt="Hero" />
      </div>

      {/* Headline */}
      <div className="mlp-text-block">
        <h1 className="mlp-heading">Empower. Engage. Excel.</h1>
        <p className="mlp-subheading">
          Revolutionizing mentorship with advanced progress tracking,
          intuitive scheduling, and effortless communication.
        </p>
      </div>

      {/* CTA Button */}
      <div className="mlp-cta">
        <Link to="/student_signup">
          <button className="mlp-get-started">GET STARTED</button>
        </Link>
      </div>

<div className="mlp-icons-section">
  <div className="mlp-icon-card">
    <img src={EfficiencyImage} alt="Efficiency" />
    <div className="mlp-icon-text">
      <p>Efficiency <br/>& Accuracy</p>
    </div>
  </div>
  <div className="mlp-icon-card">
    <img src={PersonalizationImage} alt="Personalization" />
    <div className="mlp-icon-text">
      <p>Personalization <br/>& Growth</p>
    </div>
  </div>
  <div className="mlp-icon-card">
    <img src={LearningImage} alt="Learning" />
    <div className="mlp-icon-text">
      <p>Enhanced Learning <br/>Experience</p>
    </div>
  </div>
</div>

      {/* Footer */}
      <Footer />
      <Chatbot />
    </div>
  );
};

export default MobileLandingPage;
