import React from "react";
import "../../assets/css/Privacy.css"; // Ensure CSS file is linked

const PrivacyPolicy = () => {
  return (
    <div className="privacy-container">
      <h1 className="privacy-title">Privacy Policy</h1>
      <p className="privacy-date"><strong>Effective Date:</strong> 15th March, 2025</p>
      
      <p className="privacy-intro">
        Welcome to <strong>Mentee Tracker</strong>, a platform designed to facilitate mentorship
        and personal development for students of <strong>Jain University</strong>. This Privacy
        Policy explains how we collect, use, store, and protect your information when you use our platform.
      </p>
      
      <hr className="privacy-divider" />
      
      <h2 className="privacy-heading">1. Information We Collect</h2>
      <h3 className="privacy-subheading">1.1 Student Information</h3>
      <ul className="privacy-list">
        <li className="privacy-item"><strong>Personal Information:</strong> Name, USN, email, and password.</li>
        <li className="privacy-item"><strong>Academic Details:</strong> Subjects of interest, strengths/weaknesses, fears, and goals.</li>
        <li className="privacy-item"><strong>SWOT Analysis Data:</strong> Responses for SWOT analysis generation.</li>
        <li className="privacy-item"><strong>Activity Progress Data:</strong> Updates on completed or pending activities.</li>
      </ul>
      
      <h3 className="privacy-subheading">1.2 Mentor Information</h3>
      <ul className="privacy-list">
        <li className="privacy-item"><strong>Personal Information:</strong> Name, email, department, and designation.</li>
        <li className="privacy-item"><strong>Mentorship Data:</strong> Assigned student activities, progress tracking, and feedback.</li>
      </ul>
      
      <h3 className="privacy-subheading">1.3 System & Usage Data</h3>
      <ul className="privacy-list">
        <li className="privacy-item"><strong>Device & Browser Info:</strong> IP address, browser type, OS.</li>
        <li className="privacy-item"><strong>Usage Data:</strong> Login timestamps, pages visited, and interactions.</li>
      </ul>
      
      <h2 className="privacy-heading">2. How We Use Your Information</h2>
      <ul className="privacy-list">
        <li className="privacy-item"><strong>Personalized Mentorship:</strong> SWOT analysis, activity tracking.</li>
        <li className="privacy-item"><strong>Mentor-Student Interaction:</strong> Monitoring activities, providing feedback.</li>
        <li className="privacy-item"><strong>Security & Administration:</strong> Maintaining account security, preventing fraud.</li>
        <li className="privacy-item"><strong>Communication:</strong> Notifications, mentorship updates.</li>
      </ul>
      
      <h2 className="privacy-heading">3. Data Privacy & Protection</h2>
      <h3 className="privacy-subheading">3.1 Data Security</h3>
      <ul className="privacy-list">
        <li className="privacy-item">Encryption of sensitive data (e.g., passwords, SWOT analysis).</li>
        <li className="privacy-item">Restricted access controls for authorized users only.</li>
        <li className="privacy-item">Regular security audits.</li>
      </ul>
      
      <h3 className="privacy-subheading">3.2 Confidentiality of SWOT Reports</h3>
      <ul className="privacy-list">
        <li className="privacy-item">Students’ SWOT reports are strictly confidential.</li>
        <li className="privacy-item">Mentors cannot access SWOT reports but can view activities.</li>
        <li className="privacy-item">Admins manage operations but cannot access SWOT reports.</li>
      </ul>
      
      <h2 className="privacy-heading">4. Data Retention & Deletion</h2>
      <h3 className="privacy-subheading">4.1 Data Storage</h3>
      <ul className="privacy-list">
        <li className="privacy-item">Data is stored securely on Jain University’s protected servers.</li>
        <li className="privacy-item">SWOT analysis and activity data are retained for academic purposes.</li>
      </ul>
      
      <h3 className="privacy-subheading">4.2 Account Deletion</h3>
      <ul className="privacy-list">
        <li className="privacy-item">Students can request account deletion under university guidelines.</li>
        <li className="privacy-item">Upon deletion, personal data is removed from the active database.</li>
        <li className="privacy-item">Some data may be retained temporarily for compliance reasons.</li>
      </ul>
      
      <h2 className="privacy-heading">5. User Rights & Control Over Data</h2>
      <ul className="privacy-list">
        <li className="privacy-item"><strong>Right to Access:</strong> View and download stored data.</li>
        <li className="privacy-item"><strong>Right to Update:</strong> Request corrections to inaccurate information.</li>
        <li className="privacy-item"><strong>Right to Deletion:</strong> Request account and data removal.</li>
        <li className="privacy-item"><strong>Right to Restrict Processing:</strong> Control data usage in mentorship.</li>
      </ul>
      
      <h2 className="privacy-heading">6. Changes to This Privacy Policy</h2>
      <ul className="privacy-list">
        <li className="privacy-item">Jain University reserves the right to modify this policy.</li>
        <li className="privacy-item">Users will be notified via email of significant updates.</li>
        <li className="privacy-item">Continued use of Mentee Tracker implies acceptance of changes.</li>
      </ul>
      
      <h2 className="privacy-heading">7. Contact & Support</h2>
      <ul className="privacy-list">
        <li className="privacy-item">Submit a query through the Guide Bot on the platform.</li>
        <li className="privacy-item">Use the contact form available on the website.</li>
      </ul>
    </div>
  );
};

export default PrivacyPolicy;