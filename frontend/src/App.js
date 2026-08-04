import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import PrivateRoute from './ProtectedRoute';
import LandingPage from './pages/Landing';
import LandingPageMobile from './pages/mobile/Landing';
import './assets/css/MobileResponsive.css';
import './assets/css/PixelOptimized.css';
import Appointments from './pages/mentor/components/Appointments';
import StudentSignup from './pages/auth/StudentSignup';
import Login from './pages/auth/Login';
import Logout from './pages/auth/Logout';
import ForgotPassword from './pages/auth/ForgotPassword';
import MentorDashboard from './pages/mentor/MentorDashboard';
import Profile from './pages/mentor/components/MentorProfile';
import AssignedStudents from './pages/mentor/components/AssignedStudents';
import ActivityTracking from './pages/mentor/components/ActivityTracking';
import MentorMeetings from './pages/mentor/components/Meetings';
import StudentDashboard from './pages/student/StudentDashboard';
import StudentDashboardHome from './pages/student/components/StudentDashboardHome';
import StudentProfile from './pages/student/components/StudentProfile';
import CreateStudentProfile from './pages/student/components/CreateStudentProfile';
import PsychometricForm from './pages/student/components/PsychometricForm';
import ReportPage from './pages/student/components/Report';
import ActivitiesPage from './pages/student/components/Activities';
import StudentLoggedActivities from './pages/student/components/StudentLoggedActivities';
import StudentMeetings from './pages/student/components/Meetings';
import ActivitiesSubmissions from './pages/student/components/ActivitiesSubmission';
import ActivitiesApproval from './pages/mentor/components/ActivityApproval';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminProfile from './pages/admin/components/AdminProfile';
import AdminActivities from './pages/admin/components/AdminActivities';
import AdminStudents from './pages/admin/components/AdminStudents';
import AdminCounselingDashboard from './pages/admin/components/AdminCounselingDashboard';
import LinkPage from './pages/Links';
import TermsOfService from './pages/components/TermsofService';
import PrivacyPolicy from './pages/components/PrivacyPolicy';
import StudentScheduleMeeting from './pages/student/components/Appointments';
import McaForm from './pages/student/components/McaForm'; // <-- Import MCA Form
import GenerateObservation from './pages/student/components/GenerateObservation';
import DownloadMCA from './pages/student/components/DownloadMCA';
import AcademicPerformance from './pages/student/components/AcademicPerformance';
import ExperientialLearning from './pages/student/components/ExperienceLearning';
import PF16Form from './pages/student/components/PF16Form';
import IBPForm from './pages/student/components/IBPForm';
import Counseling from './pages/student/components/Counseling';
import CounselingDashboard from './pages/mentor/components/CounselingDashboard';
import StudentsExperienceLearning from './pages/mentor/components/StudentsExperienceLearning';
import StudentDetailPage from './pages/mentor/components/StudentDetailPage';
import Chatbot from './pages/Chatbot';
import MentorAttendance from './pages/mentor/components/Attendance';
import MentorDashboardHome from './pages/mentor/components/MentorDashboardHome';
import MentorConsolidatedInternalMarks from './pages/mentor/components/MentorConsolidatedInternalMarks';
import StudentAttendance from './pages/student/components/Attendance';
import LeaderDashboard from './pages/leader/LeaderDashboard';
import LeaderStats from './pages/leader/LeaderStats';
import LeaderStudents from './pages/leader/LeaderStudents';
import LeaderMentors from './pages/leader/LeaderMentors';
import WorkingCommitteeDashboard from './pages/workingCommittee/WorkingCommitteeDashboard';
import WorkingCommitteeStats from './pages/workingCommittee/WorkingCommitteeStats';
import WorkingCommitteeDepartments from './pages/workingCommittee/WorkingCommitteeDepartments';
import WorkingCommitteeStudents from './pages/workingCommittee/WorkingCommitteeStudents';
import WorkingCommitteeMentors from './pages/workingCommittee/WorkingCommitteeMentors';
import DepartmentFacultyDashboard from './pages/departmentFaculty/DepartmentFacultyDashboard';
import DepartmentFacultyStats from './pages/departmentFaculty/DepartmentFacultyStats';
import DepartmentFacultyStudents from './pages/departmentFaculty/DepartmentFacultyStudents';
import DepartmentFacultyMentors from './pages/departmentFaculty/DepartmentFacultyMentors';
import HODDashboard from './pages/hod/HODDashboard';
import HODStats from './pages/hod/HODStats';
import HODStudents from './pages/hod/HODStudents';
import ProgramFacultyDashboard from './pages/programFaculty/ProgramFacultyDashboard';
import ProgramFacultyStats from './pages/programFaculty/ProgramFacultyStats';
import ProgramFacultyStudents from './pages/programFaculty/ProgramFacultyStudents';
import ProgramFacultyMentors from './pages/programFaculty/ProgramFacultyMentors';

const App = () => {
  return (
    <Router>
      <Chatbot />
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/mobile" element={<LandingPageMobile />} />
        <Route path="/student_signup" element={<StudentSignup />} />
        <Route path="/login" element={<Login />} />
        <Route path="/forgotpassword" element={<ForgotPassword />} />
        <Route path="/biogred" element={<LinkPage />} />
        <Route path="/logout" element={<Logout />} />
        <Route path="/terms-of-service" element={<TermsOfService />} />
        <Route path="/privacy-policy" element={<PrivacyPolicy />} />

        {/* Mentor Dashboard with Nested Routes */}
        <Route path="/mentor/:mentor_id" element={<PrivateRoute userId="mentor_id" element={<MentorDashboard />} />}>
          <Route index element={<MentorDashboardHome />} />
          <Route path="dashboard" element={<MentorDashboardHome />} />
          <Route path="profile" element={<Profile />} />
          <Route path="assigned_students" element={<AssignedStudents />} />
          <Route path="consolidated-internal-marks" element={<MentorConsolidatedInternalMarks />} />
          <Route path="activity_tracking" element={<ActivityTracking />} />
          <Route path="meetings" element={<MentorMeetings />} />
          <Route path="approvals" element={<ActivitiesApproval />} />
          <Route path="appointments" element={<Appointments />} />
          <Route path="counseling" element={<CounselingDashboard />} />
          <Route path="attendance" element={<MentorAttendance />} />
          <Route path="experience_learning" element={<StudentsExperienceLearning />} />
          <Route path="student/:student_usn" element={<StudentDetailPage />} />
        </Route>

        {/* Admin Dashboard with Nested Routes */}
        <Route path="/admin/:admin_id" element={<PrivateRoute userId="admin_id" element={<AdminDashboard />} />}>
          <Route path="profile" element={<AdminProfile />} />
          <Route path="allstudents" element={<AdminStudents />} />
          <Route path="activities" element={<AdminActivities />} />
          <Route path="counseling" element={<AdminCounselingDashboard />} />
        </Route>

        {/* Student Dashboard with Nested Routes */}
        <Route path="/student/:student_usn" element={<PrivateRoute userId="student_usn" element={<StudentDashboard />} />}>
          <Route path="dashboard" element={<StudentDashboardHome />} />
          <Route path="profile" element={<StudentProfile />} />
          <Route path="createprofile" element={<CreateStudentProfile />} />
          <Route path="psychometric" element={<PsychometricForm />} />
          <Route path="mca_form" element={<McaForm />} /> {/* <-- Add this line */}
          <Route path="report" element={<ReportPage />} />
          <Route path="activities" element={<ActivitiesPage />} />
          <Route path="logged_activities" element={<StudentLoggedActivities />} />
          <Route path="scheduled_meetings" element={<StudentMeetings />} />
          <Route path="submissions" element={<ActivitiesSubmissions />} />
          <Route path="appointments" element={<StudentScheduleMeeting />} />
          <Route path="counseling" element={<Counseling />} />
          <Route path="attendance" element={<StudentAttendance />} />
          <Route path="academic-performance" element={<AcademicPerformance />} />
          <Route path="experiential-learning" element={<ExperientialLearning />} />
          <Route path="pf16-form" element={<PF16Form />} />
          <Route path="ibp-form" element={<IBPForm />} />
          <Route path="generate_observation" element={<GenerateObservation />} />
          <Route path="download_mca" element={<DownloadMCA />} />
        </Route>

        {/* Leader Dashboard */}
        <Route path="/leader/:leader_id" element={<PrivateRoute userId="leader_id" requiredRole="leader" element={<LeaderDashboard />} />}>
          <Route index element={<LeaderStats />} />
          <Route path="students" element={<LeaderStudents />} />
          <Route path="mentors" element={<LeaderMentors />} />
        </Route>

        {/* Working Committee Dashboard (second stage: 3 members, each with allocated departments) */}
        <Route path="/working-committee/:member_id" element={<PrivateRoute userId="member_id" requiredRole="working_committee" element={<WorkingCommitteeDashboard />} />}>
          <Route index element={<WorkingCommitteeStats />} />
          <Route path="departments" element={<WorkingCommitteeDepartments />} />
          <Route path="students" element={<WorkingCommitteeStudents />} />
          <Route path="mentors" element={<WorkingCommitteeMentors />} />
        </Route>

        {/* Department Faculty Dashboard */}
        <Route path="/department-faculty/:member_id" element={<PrivateRoute userId="member_id" requiredRole="department_faculty" element={<DepartmentFacultyDashboard />} />}>
          <Route index element={<DepartmentFacultyStats />} />
          <Route path="students" element={<DepartmentFacultyStudents />} />
          <Route path="mentors" element={<DepartmentFacultyMentors />} />
        </Route>

        {/* HOD Dashboard */}
        <Route path="/hod/:member_id" element={<PrivateRoute userId="member_id" requiredRole="hod" element={<HODDashboard />} />}>
          <Route index element={<HODStats />} />
          <Route path="students" element={<HODStudents />} />
        </Route>

        {/* Program Faculty Dashboard */}
        <Route path="/program-faculty/:member_id" element={<PrivateRoute userId="member_id" requiredRole="program_faculty" element={<ProgramFacultyDashboard />} />}>
          <Route index element={<ProgramFacultyStats />} />
          <Route path="students" element={<ProgramFacultyStudents />} />
          <Route path="mentors" element={<ProgramFacultyMentors />} />
        </Route>
      </Routes>
    </Router>
  );
};

export default App;