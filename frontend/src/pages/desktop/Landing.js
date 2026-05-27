import React from 'react';
import { Link } from 'react-router-dom';
import '../../assets/css/Landing.css';
import EfficiencyImage from '../../assets/images/efficiency.png';
import PersonalizationImage from '../../assets/images/personalization.png';
import LearningImage from '../../assets/images/learning.png';
import HeroImage from '../../assets/images/hero.png';
import Chatbot from '../Chatbot';
import Footer from '../components/Footer';

const MENTEE_TRACKER_LOGO_URL = 'https://jgi-menteetrackers.s3.ap-south-1.amazonaws.com/logo_mentee-removebg-preview.png';
const JAIN_LOGO_URL = 'https://jgi-menteetrackers.s3.ap-south-1.amazonaws.com/Jain-Logo.png';

const LandingPage = React.memo(() => {
  return (
      <div className="lp-landing-page">
        <div className='lp-headers'>
          <Link to="/" className="lp-logo-left" aria-label="Mentee Tracker home">
            <img src={MENTEE_TRACKER_LOGO_URL} alt="Mentee Tracker" className="lp-logo-img" />
          </Link>
          <div className="lp-logo-right">
            <img src={JAIN_LOGO_URL} alt="Jain University" className="lp-logo-img" />
          </div>
        </div>
        <div className="lp-content">
          <div className="lp-text-section">
            <h1 className="lp-heading">Empower. Engage.<br />Excel.</h1>
            <p className="lp-paragraph lp-paragraph-primary">
              Revolutionizing mentorship with advanced<br />
              progress tracking, intuitive scheduling,<br />
              and effortless communication.
            </p>
          </div>
          <div className="lp-image-section" style={{ backgroundImage: `url(${HeroImage})` }}></div>

          <div className="lp-login-buttons">
            <Link to="/student_signup">
              <button className="lp-login-button">Get Started</button>
            </Link>
          </div>

          <div className="lp-icon-section">
            <div className="lp-icon-item">
              <img src={EfficiencyImage} alt="Efficiency" className="lp-icon" />
              <p className="lp-icon-description">Efficiency <br />& Accuracy</p>
            </div>
            <div className="lp-icon-item">
              <img src={PersonalizationImage} alt="Personalization" className="lp-icon" />
              <p className="lp-icon-description">Personalization <br />& Growth</p>
            </div>
            <div className="lp-icon-item">
              <img src={LearningImage} alt="Enhanced Learning" className="lp-icon" />
              <p className="lp-icon-description">Enhanced Learning <br />Experience</p>
            </div>
          </div>
        </div>
        <Footer/>
        <Chatbot/>
      </div>
  );
});

LandingPage.displayName = 'LandingPage';

export default LandingPage;