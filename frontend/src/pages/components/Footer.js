import React from "react";

const MENTEE_TRACKER_LOGO_URL = 'https://res.cloudinary.com/dvlitilou/image/upload/v1779924617/logo_mentee-removebg-preview_coyhds.png';
const JAIN_LOGO_URL = 'https://res.cloudinary.com/dvlitilou/image/upload/v1779924616/Jain-Logo_jix84i.png';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="lp-footer-container">
      <div className="lp-footer-left">
        <ul className="lp-footer-links">
          <li>
            <a href="/about" className="lp-footer-link">About Us</a>
          </li>
          <span>|</span>
          <li>
            <a href="/terms" className="lp-footer-link">Terms of Service</a>
          </li>
          <span>|</span>
          <li>
            <a href="/privacy" className="lp-footer-link">Privacy Policy</a>
          </li>
          <span>|</span>
          <li>
            <a href="/contact" className="lp-footer-link">Contact</a>
          </li>
        </ul>
      </div>
      <div className="lp-footer-right">
        <span className="lp-footer-logos">
          <img src={MENTEE_TRACKER_LOGO_URL} alt="Mentee Tracker" className="lp-footer-logo lp-footer-logo-mentee" />
          <img src={JAIN_LOGO_URL} alt="Jain University" className="lp-footer-logo lp-footer-logo-jain" />
        </span>
        &copy; {currentYear} <a href="https://krintix.com" className="lp-footer-linkb">KRINTIX</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;All rights reserved.
      </div>
    </footer>
  );
};

export default Footer;
