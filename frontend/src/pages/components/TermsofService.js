import React from "react";
import "../../assets/css/Terms.css"; // Ensure CSS file is linked

const TermsOfService = () => {
  return (
    <div className="terms-container">
      <h1 className="terms-title">Terms of Service</h1>
      <p className="terms-date"><strong>Effective Date:</strong> 15th March, 2025</p>

      <p className="terms-intro">
        Welcome to <strong>Mentee Tracker</strong>, a mentoring and progress-tracking platform 
        exclusively designed for students and mentors of <strong>Jain University</strong>. By accessing 
        or using Mentee Tracker, you agree to comply with the following <strong>Terms of Service</strong>. 
        If you do not agree, please <strong>do not use the platform</strong>.
      </p>

      <hr className="terms-divider" />

      <h2 className="terms-heading">1. Acceptance of Terms</h2>
      <ul className="terms-list">
        <li className="terms-item">Mentee Tracker is exclusively available to <strong>registered students and mentors of Jain University</strong>.</li>
        <li className="terms-item">By signing up or accessing the platform, you <strong>agree to these Terms of Service</strong> and future modifications.</li>
        <li className="terms-item">Unauthorized access or use by individuals <strong>not affiliated with Jain University</strong> is strictly prohibited.</li>
      </ul>

      <h2 className="terms-heading">2. User Accounts & Responsibilities</h2>
      
      <h3 className="terms-subheading">2.1 Student Accounts</h3>
      <ul className="terms-list">
        <li className="terms-item">Students <strong>must create an account</strong> using their <strong>USN (University Serial Number), email, and password</strong>.</li>
        <li className="terms-item">Students are responsible for <strong>keeping login credentials secure</strong>.</li>
        <li className="terms-item">Unauthorized access or misuse must be <strong>reported immediately</strong> to support.</li>
      </ul>

      <h3 className="terms-subheading">2.2 Mentor Accounts</h3>
      <ul className="terms-list">
        <li className="terms-item">Mentors are <strong>pre-registered</strong> in the system by <strong>Jain University</strong>.</li>
        <li className="terms-item">They must use their <strong>assigned credentials</strong> to access the platform.</li>
      </ul>

      <h3 className="terms-subheading">2.3 Data Privacy & Access Control</h3>
      <ul className="terms-list">
        <li className="terms-item">Students’ personal information, SWOT reports, and progress data are kept <strong>strictly confidential</strong>.</li>
        <li className="terms-item">Mentors <strong>cannot access students' SWOT reports</strong>.</li>
        <li className="terms-item">Admins manage platform operations but <strong>cannot access students' SWOT reports</strong> for privacy reasons.</li>
      </ul>

      <h2 className="terms-heading">3. Platform Usage Rules</h2>

      <h3 className="terms-subheading">3.1 Student Responsibilities</h3>
      <ul className="terms-list">
        <li className="terms-item">Students <strong>must provide honest responses</strong> for accurate SWOT analysis.</li>
        <li className="terms-item">Students must <strong>actively engage</strong> in assigned activities.</li>
        <li className="terms-item">Proof of activity completion (such as <strong>drive links</strong>) must be uploaded for verification.</li>
      </ul>

      <h3 className="terms-subheading">3.2 Mentor Responsibilities</h3>
      <ul className="terms-list">
        <li className="terms-item">Mentors <strong>can track activities</strong> but <strong>cannot access SWOT reports</strong>.</li>
        <li className="terms-item">They must <strong>monitor progress, schedule meetings, provide resources, and verify activities</strong>.</li>
      </ul>

      <h3 className="terms-subheading">3.3 General Rules</h3>
      <ul className="terms-list">
        <li className="terms-item"><strong>Users must not share login credentials</strong> or access unauthorized data.</li>
        <li className="terms-item"><strong>All communication must be professional</strong>.</li>
        <li className="terms-item">Misuse may result in <strong>suspension or termination</strong>.</li>
      </ul>

      <h2 className="terms-heading">4. Data Privacy & Security</h2>
      <h3 className="terms-subheading">4.1 Data Access & Permissions</h3>
      <ul className="terms-list">
        <li className="terms-item">Students have access to their <strong>profile, SWOT report, and progress</strong>.</li>
        <li className="terms-item">Mentors can view students' <strong>profile and activity progress</strong>.</li>
        <li className="terms-item">Admins oversee platform management but <strong>cannot view SWOT reports</strong>.</li>
      </ul>

      <h3 className="terms-subheading">4.2 Security Measures</h3>
      <ul className="terms-list">
        <li className="terms-item">User data is <strong>encrypted and securely stored</strong>.</li>
        <li className="terms-item">Strict <strong>access control policies</strong> prevent unauthorized access.</li>
      </ul>

      <h3 className="terms-subheading">4.3 Data Modification & Deletion</h3>
      <ul className="terms-list">
        <li className="terms-item">Students can request <strong>profile updates</strong>.</li>
        <li className="terms-item">Account deletion requests follow Jain University’s <strong>data retention policy</strong>.</li>
      </ul>

      <p className="terms-footer">
        <strong>By using Mentee Tracker, you confirm that you have read, understood, and agreed to these Terms of Service.</strong>
      </p>
    </div>
  );
};

export default TermsOfService;
