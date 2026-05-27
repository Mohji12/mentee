import React, { useState, useEffect, useMemo } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../../../api';
import '../../../assets/css/LeaderDashboard.css';
import './MentorDashboardHome.css';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import { 
  FaCalendarPlus, 
  FaUserClock, 
  FaTasks, 
  FaEnvelope,
  FaBell,
  FaExclamationTriangle,
  FaInfoCircle,
  FaChevronDown,
  FaChevronUp,
  FaSearch,
  FaFilter,
  FaDownload,
  FaCalendarAlt,
  FaClipboardList,
  FaChartPie,
  FaCheckCircle,
  FaClock,
  FaUserGraduate,
  FaChevronLeft,
  FaChevronRight,
  FaUsers,
  FaCalendarCheck,
  FaUserCheck,
  FaClipboardCheck,
  FaChartLine,
  FaHandsHelping,
  FaGraduationCap,
  FaFileAlt,
  FaPercentage,
  FaArrowUp,
  FaArrowDown
} from 'react-icons/fa';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const MentorDashboardHome = () => {
  const { mentor_id } = useParams();
  const navigate = useNavigate();
  const [assignedStudents, setAssignedStudents] = useState([]);
  const [pendingMeetings, setPendingMeetings] = useState([]);
  const [attendanceStats, setAttendanceStats] = useState(null);
  const [studentStats, setStudentStats] = useState(null);
  const [meetingsTotal, setMeetingsTotal] = useState(null);
  const [activitiesTotal, setActivitiesTotal] = useState(null);
  const [submissionsTotal, setSubmissionsTotal] = useState(null);
  const [counselingTotal, setCounselingTotal] = useState(null);
  const [experientialTotal, setExperientialTotal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Email state
  const [emailStudentUsn, setEmailStudentUsn] = useState('');
  const [emailSubject, setEmailSubject] = useState('');
  const [emailMessage, setEmailMessage] = useState('');
  const [emailSending, setEmailSending] = useState(false);
  const [emailResult, setEmailResult] = useState(null);
  
  // New dashboard states
  const [alerts, setAlerts] = useState({ alerts: [], summary: { total: 0 } });
  const [alertsExpanded, setAlertsExpanded] = useState(true);
  const [activityFeed, setActivityFeed] = useState([]);
  const [atRiskStudents, setAtRiskStudents] = useState([]);
  const [attendanceTrend, setAttendanceTrend] = useState({ trend: [], labels: [] });
  const [emailHistory, setEmailHistory] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [calendarEvents, setCalendarEvents] = useState([]);
  const [formCompletionStats, setFormCompletionStats] = useState(null);
  
  // Search and filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [sortBy, setSortBy] = useState('usn');
  const [sortOrder, setSortOrder] = useState('asc');
  
  // Calendar state
  const [calendarWeekOffset, setCalendarWeekOffset] = useState(0);

  useEffect(() => {
    const token = sessionStorage.getItem('access_token');
    const fetchData = async () => {
      setLoading(true);
      setError('');
      try {
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        
        const [
          studentsRes,
          meetingsRes,
          statsRes,
          studentStatsRes,
          meetingsListRes,
          activitiesRes,
          submissionsRes,
          counselingStatsRes,
          experientialRes,
          alertsRes,
          activityFeedRes,
          atRiskRes,
          trendRes,
          calendarRes,
          formStatsRes,
          emailHistoryRes
        ] = await Promise.all([
          fetch(`${API_BASE_URL}/mentor/${mentor_id}/assigned_students`, { headers }),
          fetch(`${API_BASE_URL}/mentor/${mentor_id}/pending_meetings`, { headers }),
          fetch(`${API_BASE_URL}/mentor/${mentor_id}/attendance/stats`, { headers }),
          fetch(`${API_BASE_URL}/mentor/${mentor_id}/student_stats`, { headers }),
          fetch(`${API_BASE_URL}/mentor/${mentor_id}/meetings`),
          fetch(`${API_BASE_URL}/mentor/${mentor_id}/activities`),
          fetch(`${API_BASE_URL}/mentor/${mentor_id}/submissions`),
          fetch(`${API_BASE_URL}/mentor/${mentor_id}/counseling/stats`, { headers }),
          fetch(`${API_BASE_URL}/mentor/${mentor_id}/students/experience-learning`, { headers }),
          fetch(`${API_BASE_URL}/mentor/${mentor_id}/dashboard/alerts`, { headers }),
          fetch(`${API_BASE_URL}/mentor/${mentor_id}/dashboard/activity-feed`, { headers }),
          fetch(`${API_BASE_URL}/mentor/${mentor_id}/dashboard/at-risk-students`, { headers }),
          fetch(`${API_BASE_URL}/mentor/${mentor_id}/dashboard/attendance-trend`, { headers }),
          fetch(`${API_BASE_URL}/mentor/${mentor_id}/dashboard/calendar-events`, { headers }),
          fetch(`${API_BASE_URL}/mentor/${mentor_id}/dashboard/form-completion-stats`, { headers }),
          fetch(`${API_BASE_URL}/mentor/${mentor_id}/email-history`, { headers })
        ]);

        if (studentsRes.ok) {
          const data = await studentsRes.json();
          setAssignedStudents(Array.isArray(data) ? data : []);
        } else {
          setAssignedStudents([]);
        }

        if (meetingsRes.ok) {
          const data = await meetingsRes.json();
          setPendingMeetings(Array.isArray(data) ? data : []);
        } else {
          setPendingMeetings([]);
        }

        if (statsRes.ok) {
          setAttendanceStats(await statsRes.json());
        }

        if (studentStatsRes.ok) {
          setStudentStats(await studentStatsRes.json());
        }

        if (meetingsListRes.ok) {
          const data = await meetingsListRes.json();
          setMeetingsTotal(Array.isArray(data.meetings) ? data.meetings.length : null);
        }

        if (activitiesRes.ok) {
          const data = await activitiesRes.json();
          setActivitiesTotal(Array.isArray(data) ? data.length : null);
        }

        if (submissionsRes.ok) {
          const data = await submissionsRes.json();
          setSubmissionsTotal(Array.isArray(data) ? data.length : null);
        }

        if (counselingStatsRes.ok) {
          const data = await counselingStatsRes.json();
          setCounselingTotal(typeof data.total_sessions === 'number' ? data.total_sessions : null);
        }

        if (experientialRes.ok) {
          const data = await experientialRes.json();
          setExperientialTotal(Array.isArray(data) ? data.length : null);
        }

        // New dashboard data
        if (alertsRes.ok) {
          setAlerts(await alertsRes.json());
        }

        if (activityFeedRes.ok) {
          const data = await activityFeedRes.json();
          setActivityFeed(data.activities || []);
        }

        if (atRiskRes.ok) {
          const data = await atRiskRes.json();
          console.log('At-Risk Students API Response:', data);
          setAtRiskStudents(data.at_risk_students || []);
        } else {
          console.error('At-Risk Students API failed:', atRiskRes.status, atRiskRes.statusText);
        }

        if (trendRes.ok) {
          setAttendanceTrend(await trendRes.json());
        }

        if (calendarRes.ok) {
          const data = await calendarRes.json();
          console.log('Calendar Events API Response:', data);
          setCalendarEvents(data.events || []);
        } else {
          console.error('Calendar Events API failed:', calendarRes.status, calendarRes.statusText);
        }

        if (formStatsRes.ok) {
          const data = await formStatsRes.json();
          console.log('Form Completion Stats API Response:', data);
          setFormCompletionStats(data);
        } else {
          console.error('Form Completion Stats API failed:', formStatsRes.status, formStatsRes.statusText);
        }

        if (emailHistoryRes.ok) {
          const data = await emailHistoryRes.json();
          setEmailHistory(data.emails || []);
        }

      } catch (e) {
        setError(e.message || 'Failed to load dashboard data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [mentor_id]);

  const refreshEmailHistory = async () => {
    const token = sessionStorage.getItem('access_token');
    try {
      const res = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/email-history`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });
      if (res.ok) {
        const data = await res.json();
        setEmailHistory(data.emails || []);
      }
    } catch (e) {
      console.error('Failed to refresh email history:', e);
    }
  };

  const handleSendEmail = async (e) => {
    e.preventDefault();
    if (!emailStudentUsn || !emailSubject.trim() || !emailMessage.trim()) {
      setEmailResult({ success: false, message: 'Please select a student, and enter subject and message.' });
      return;
    }
    setEmailSending(true);
    setEmailResult(null);
    const token = sessionStorage.getItem('access_token');
    try {
      const res = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/send-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          student_usn: emailStudentUsn,
          subject: emailSubject.trim(),
          message: emailMessage.trim(),
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok && data.success) {
        setEmailResult({ success: true, message: data.message || 'Email sent.' });
        setEmailSubject('');
        setEmailMessage('');
        setEmailStudentUsn('');
        // Refresh email history after successful send
        refreshEmailHistory();
      } else {
        setEmailResult({
          success: false,
          message: data.detail || 'Failed to send email. Please try again.',
        });
      }
    } catch (err) {
      setEmailResult({ success: false, message: 'Failed to send email. Please try again.' });
    } finally {
      setEmailSending(false);
    }
  };

  const formatEmailDate = (dateStr) => {
    if (!dateStr) return 'Unknown';
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  // Process student form completion data
  const perStudentFormRows = useMemo(() => {
    return assignedStudents.map((s) => {
      const rawStatus = typeof s.status === 'string' ? s.status : '';
      const statusLower = rawStatus.toLowerCase();
      const completeFlow = statusLower.includes('complete flow');

      return {
        student_usn: s.student_usn,
        student_name: s.student_name,
        statusText: rawStatus || 'Not Started',
        signedUp: completeFlow || statusLower.includes('signed up'),
        profileCreated: completeFlow || statusLower.includes('profile created'),
        psychometricFilled: completeFlow || statusLower.includes('form filled'),
        swotGenerated: completeFlow || statusLower.includes('swot generated'),
        activitiesGenerated: completeFlow || statusLower.includes('activities generated'),
        mcaFilled: completeFlow || statusLower.includes('mca form filled'),
        pf16Filled: completeFlow || statusLower.includes('16pf filled'),
        ibpFilled: completeFlow || statusLower.includes('ibp filled'),
      };
    });
  }, [assignedStudents]);

  // Filter and sort students
  const filteredAndSortedRows = useMemo(() => {
    let rows = [...perStudentFormRows];
    
    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      rows = rows.filter(r => 
        r.student_usn.toLowerCase().includes(query) || 
        (r.student_name && r.student_name.toLowerCase().includes(query))
      );
    }
    
    // Apply status filter
    if (filterStatus !== 'all') {
      if (filterStatus === 'complete') {
        rows = rows.filter(r => r.statusText.toLowerCase().includes('complete flow'));
      } else if (filterStatus === 'incomplete') {
        rows = rows.filter(r => !r.statusText.toLowerCase().includes('complete flow'));
      } else if (filterStatus === 'no_profile') {
        rows = rows.filter(r => !r.profileCreated);
      }
    }
    
    // Apply sorting
    rows.sort((a, b) => {
      let comparison = 0;
      if (sortBy === 'usn') {
        comparison = a.student_usn.localeCompare(b.student_usn);
      } else if (sortBy === 'name') {
        comparison = (a.student_name || '').localeCompare(b.student_name || '');
      } else if (sortBy === 'status') {
        comparison = a.statusText.localeCompare(b.statusText);
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });
    
    return rows;
  }, [perStudentFormRows, searchQuery, filterStatus, sortBy, sortOrder]);

  // Export to CSV
  const handleExportCSV = () => {
    const headers = ['USN', 'Name', 'Signed Up', 'Profile', 'Psychometric', 'SWOT', 'Activities', 'MCA', '16PF', 'IBP', 'Status'];
    const csvData = filteredAndSortedRows.map(r => [
      r.student_usn,
      r.student_name || '',
      r.signedUp ? 'Yes' : 'No',
      r.profileCreated ? 'Yes' : 'No',
      r.psychometricFilled ? 'Yes' : 'No',
      r.swotGenerated ? 'Yes' : 'No',
      r.activitiesGenerated ? 'Yes' : 'No',
      r.mcaFilled ? 'Yes' : 'No',
      r.pf16Filled ? 'Yes' : 'No',
      r.ibpFilled ? 'Yes' : 'No',
      r.statusText
    ]);
    
    const csvContent = [headers, ...csvData].map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `mentee_progress_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  // Chart configurations
  const attendanceChartData = {
    labels: attendanceTrend.labels || [],
    datasets: [{
      label: 'Attendance %',
      data: (attendanceTrend.trend || []).map(t => t.percentage),
      fill: true,
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4,
      pointBackgroundColor: '#3b82f6',
    }]
  };

  const attendanceChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      title: { display: true, text: 'Weekly Attendance Trend', font: { size: 14 } }
    },
    scales: {
      y: { beginAtZero: true, max: 100, ticks: { callback: v => v + '%' } }
    }
  };

  const formCompletionChartData = useMemo(() => {
    if (!formCompletionStats?.forms) return null;
    const forms = formCompletionStats.forms;
    const completed = Object.values(forms).reduce((sum, f) => sum + f.completed, 0);
    const pending = Object.values(forms).reduce((sum, f) => sum + f.pending, 0);
    
    return {
      labels: ['Completed', 'Pending'],
      datasets: [{
        data: [completed, pending],
        backgroundColor: ['#10b981', '#f59e0b'],
        borderWidth: 0,
      }]
    };
  }, [formCompletionStats]);

  const formCompletionChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom' },
      title: { display: true, text: 'Form Completion Overview', font: { size: 14 } }
    },
    cutout: '60%'
  };

  const formBreakdownChartData = useMemo(() => {
    if (!formCompletionStats?.forms) return null;
    const forms = formCompletionStats.forms;
    
    return {
      labels: Object.keys(forms),
      datasets: [{
        label: 'Completed',
        data: Object.values(forms).map(f => f.completed),
        backgroundColor: '#10b981',
      }, {
        label: 'Pending',
        data: Object.values(forms).map(f => f.pending),
        backgroundColor: '#ef4444',
      }]
    };
  }, [formCompletionStats]);

  const formBreakdownChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom' },
      title: { display: true, text: 'Form-wise Completion', font: { size: 14 } }
    },
    scales: {
      x: { stacked: true },
      y: { stacked: true, beginAtZero: true }
    }
  };

  // Calendar helpers
  const getWeekDays = () => {
    const today = new Date();
    const startOfWeek = new Date(today);
    startOfWeek.setDate(today.getDate() - today.getDay() + (calendarWeekOffset * 7));
    
    const days = [];
    for (let i = 0; i < 7; i++) {
      const day = new Date(startOfWeek);
      day.setDate(startOfWeek.getDate() + i);
      days.push(day);
    }
    return days;
  };

  const weekDays = getWeekDays();
  const today = new Date().toISOString().split('T')[0];

  const getEventsForDay = (date) => {
    const dateStr = date.toISOString().split('T')[0];
    return calendarEvents.filter(e => e.date === dateStr);
  };

  if (loading) {
    return (
      <div className="mentor-dashboard-home leader-dashboard">
        <div className="mentor-dashboard-home__loading">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mentor-dashboard-home leader-dashboard">
        <div className="mentor-dashboard-home__error" role="alert">{error}</div>
      </div>
    );
  }

  // Calculate additional metrics
  const totalStudents = assignedStudents.length;
  const profileCompletedCount = perStudentFormRows.filter(r => r.profileCreated).length;
  const psychometricCompletedCount = perStudentFormRows.filter(r => r.psychometricFilled).length;
  const swotCompletedCount = perStudentFormRows.filter(r => r.swotGenerated).length;
  const mcaCompletedCount = perStudentFormRows.filter(r => r.mcaFilled).length;
  const completeFlowCount = perStudentFormRows.filter(r => r.statusText.toLowerCase().includes('complete flow')).length;
  const overallCompletionRate = totalStudents > 0 ? Math.round((completeFlowCount / totalStudents) * 100) : 0;
  const attendanceRate = attendanceStats?.total_records > 0 
    ? Math.round(((attendanceStats?.present_count || 0) / attendanceStats.total_records) * 100) 
    : 0;

  const summaryCards = [
    { 
      label: 'Total Mentees', 
      value: totalStudents, 
      to: `/mentor/${mentor_id}/assigned_students`,
      icon: FaUsers,
      color: 'blue',
      subtitle: 'Assigned to you'
    },
    { 
      label: 'Pending Appointments', 
      value: pendingMeetings.length, 
      to: `/mentor/${mentor_id}/appointments`,
      icon: FaCalendarCheck,
      color: pendingMeetings.length > 0 ? 'orange' : 'green',
      subtitle: pendingMeetings.length > 0 ? 'Needs attention' : 'All clear'
    },
    { 
      label: 'This Week Attendance', 
      value: attendanceStats?.this_week_present ?? 0, 
      to: `/mentor/${mentor_id}/attendance`,
      icon: FaUserCheck,
      color: 'teal',
      subtitle: 'Present this week'
    },
    { 
      label: 'Attendance Rate', 
      value: `${attendanceRate}%`, 
      to: `/mentor/${mentor_id}/attendance`,
      icon: FaPercentage,
      color: attendanceRate >= 75 ? 'green' : attendanceRate >= 50 ? 'orange' : 'red',
      subtitle: attendanceRate >= 75 ? 'Good' : 'Needs improvement'
    },
    { 
      label: 'Scheduled Meetings', 
      value: meetingsTotal ?? 0, 
      to: `/mentor/${mentor_id}/meetings`,
      icon: FaCalendarAlt,
      color: 'purple',
      subtitle: 'Total meetings'
    },
    { 
      label: 'Activities Assigned', 
      value: activitiesTotal ?? 0, 
      to: `/mentor/${mentor_id}/activity_tracking`,
      icon: FaTasks,
      color: 'indigo',
      subtitle: 'Track progress'
    },
    { 
      label: 'Submissions', 
      value: submissionsTotal ?? 0, 
      to: `/mentor/${mentor_id}/approvals`,
      icon: FaClipboardCheck,
      color: 'cyan',
      subtitle: 'Activity submissions'
    },
    { 
      label: 'Student Support', 
      value: counselingTotal ?? 0, 
      to: `/mentor/${mentor_id}/counseling`,
      icon: FaHandsHelping,
      color: 'pink',
      subtitle: 'Counseling sessions'
    },
    { 
      label: 'Experiential Learning', 
      value: experientialTotal ?? 0, 
      to: `/mentor/${mentor_id}/experience_learning`,
      icon: FaGraduationCap,
      color: 'amber',
      subtitle: 'Learning entries'
    },
    { 
      label: 'Profile Completed', 
      value: `${profileCompletedCount}/${totalStudents}`, 
      to: `/mentor/${mentor_id}/assigned_students`,
      icon: FaUserGraduate,
      color: profileCompletedCount === totalStudents ? 'green' : 'orange',
      subtitle: totalStudents > 0 ? `${Math.round((profileCompletedCount/totalStudents)*100)}% complete` : 'No students'
    },
    { 
      label: 'Psychometric Forms', 
      value: `${psychometricCompletedCount}/${totalStudents}`, 
      to: `/mentor/${mentor_id}/assigned_students`,
      icon: FaClipboardList,
      color: psychometricCompletedCount === totalStudents ? 'green' : 'blue',
      subtitle: totalStudents > 0 ? `${Math.round((psychometricCompletedCount/totalStudents)*100)}% filled` : 'No students'
    },
    { 
      label: 'SWOT Generated', 
      value: `${swotCompletedCount}/${totalStudents}`, 
      to: `/mentor/${mentor_id}/assigned_students`,
      icon: FaChartPie,
      color: swotCompletedCount === totalStudents ? 'green' : 'purple',
      subtitle: totalStudents > 0 ? `${Math.round((swotCompletedCount/totalStudents)*100)}% done` : 'No students'
    },
    { 
      label: 'MCA Forms', 
      value: `${mcaCompletedCount}/${totalStudents}`, 
      to: `/mentor/${mentor_id}/assigned_students`,
      icon: FaFileAlt,
      color: mcaCompletedCount === totalStudents ? 'green' : 'teal',
      subtitle: totalStudents > 0 ? `${Math.round((mcaCompletedCount/totalStudents)*100)}% filled` : 'No students'
    },
    { 
      label: '16PF Forms', 
      value: studentStats?.pf16_filled ?? 0, 
      to: `/mentor/${mentor_id}/assigned_students`,
      icon: FaFileAlt,
      color: 'indigo',
      subtitle: 'Personality assessment'
    },
    { 
      label: 'IBP Forms', 
      value: studentStats?.ibp_filled ?? 0, 
      to: `/mentor/${mentor_id}/assigned_students`,
      icon: FaFileAlt,
      color: 'violet',
      subtitle: 'Interest battery'
    },
    { 
      label: 'Complete Flow', 
      value: `${completeFlowCount}/${totalStudents}`, 
      to: `/mentor/${mentor_id}/assigned_students`,
      icon: FaCheckCircle,
      color: completeFlowCount === totalStudents ? 'green' : 'orange',
      subtitle: `${overallCompletionRate}% completed all steps`
    },
  ];

  return (
    <div className="mentor-dashboard-home leader-dashboard">
      {/* Header with Quick Actions */}
      <header className="leader-dashboard__header mentor-dashboard-home__header">
        <div className="mdh-header-content">
          <div>
            <h1 className="leader-dashboard__title">Dashboard</h1>
            <p className="leader-dashboard__subtitle">Monitor your mentees and tasks</p>
          </div>
        </div>
        
        {/* Quick Actions Bar */}
        <div className="mdh-quick-actions">
          <button className="mdh-quick-action-btn mdh-quick-action-btn--primary" onClick={() => navigate(`/mentor/${mentor_id}/meetings`)}>
            <FaCalendarPlus /> Schedule Meeting
          </button>
          <button className="mdh-quick-action-btn mdh-quick-action-btn--secondary" onClick={() => navigate(`/mentor/${mentor_id}/attendance`)}>
            <FaUserClock /> Mark Attendance
          </button>
          <button className="mdh-quick-action-btn mdh-quick-action-btn--secondary" onClick={() => navigate(`/mentor/${mentor_id}/activity_tracking`)}>
            <FaTasks /> Assign Activity
          </button>
          <button className="mdh-quick-action-btn mdh-quick-action-btn--secondary" onClick={() => document.getElementById('email-section')?.scrollIntoView({ behavior: 'smooth' })}>
            <FaEnvelope /> Send Email
          </button>
        </div>
      </header>

      {/* Alerts Section */}
      {alerts.summary.total > 0 && (
        <section className="mdh-alerts-section">
          <div className="mdh-alerts-header" onClick={() => setAlertsExpanded(!alertsExpanded)}>
            <div className="mdh-alerts-title">
              <FaBell className="mdh-alerts-icon" />
              <span>Alerts & Notifications</span>
              <span className="mdh-alerts-badge">{alerts.summary.total}</span>
            </div>
            {alertsExpanded ? <FaChevronUp /> : <FaChevronDown />}
          </div>
          {alertsExpanded && (
            <div className="mdh-alerts-content">
              {alerts.alerts.map((alert, idx) => (
                <div key={idx} className={`mdh-alert-item mdh-alert-item--${alert.priority}`}>
                  <div className="mdh-alert-icon">
                    {alert.priority === 'urgent' && <FaExclamationTriangle />}
                    {alert.priority === 'warning' && <FaExclamationTriangle />}
                    {alert.priority === 'info' && <FaInfoCircle />}
                  </div>
                  <div className="mdh-alert-text">
                    <strong>{alert.title}</strong>
                    <p>{alert.message}</p>
                  </div>
                  {alert.action_url && (
                    <Link to={alert.action_url} className="mdh-alert-action">View</Link>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* KPI Cards */}
      <div className="mdh-kpi-grid">
        {summaryCards.map((card) => {
          const IconComponent = card.icon;
          return (
            <Link key={card.label} to={card.to} className={`mdh-kpi-card mdh-kpi-card--${card.color}`}>
              <div className="mdh-kpi-icon">
                <IconComponent />
              </div>
              <div className="mdh-kpi-content">
                <div className="mdh-kpi-value">{card.value}</div>
                <div className="mdh-kpi-label">{card.label}</div>
                {card.subtitle && <div className="mdh-kpi-subtitle">{card.subtitle}</div>}
              </div>
              <div className="mdh-kpi-arrow">
                <FaChevronRight />
              </div>
            </Link>
          );
        })}
      </div>

      {/* Charts Section */}
      <section className="mdh-charts-section">
        <div className="mdh-charts-grid">
          <div className="mdh-chart-card">
            <div className="mdh-chart-container">
              <Line data={attendanceChartData} options={attendanceChartOptions} />
            </div>
          </div>
          
          {formCompletionChartData && (
            <div className="mdh-chart-card">
              <div className="mdh-chart-container">
                <Doughnut data={formCompletionChartData} options={formCompletionChartOptions} />
              </div>
            </div>
          )}
          
          {formBreakdownChartData && (
            <div className="mdh-chart-card">
              <div className="mdh-chart-container">
                <Bar data={formBreakdownChartData} options={formBreakdownChartOptions} />
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Two Column Section: At-Risk Students + Activity Feed + Calendar */}
      <section className="mdh-two-column-section">
        <div className="mdh-column">
          {/* At-Risk Students */}
          <div className="mdh-section-card">
            <div className="mdh-section-header">
              <h3><FaExclamationTriangle className="mdh-section-icon mdh-icon-warning" /> At-Risk Students</h3>
              <span className="mdh-section-badge">{atRiskStudents.length}</span>
            </div>
            <div className="mdh-section-content">
              {atRiskStudents.length === 0 ? (
                <p className="mdh-empty-text">No at-risk students identified. Great job!</p>
              ) : (
                <div className="mdh-at-risk-list">
                  {atRiskStudents.slice(0, 5).map((student, idx) => (
                    <div key={idx} className={`mdh-at-risk-item mdh-risk-${student.risk_level}`}>
                      <div className="mdh-at-risk-info">
                        <FaUserGraduate className="mdh-at-risk-avatar" />
                        <div>
                          <strong>{student.student_name}</strong>
                          <span className="mdh-at-risk-usn">{student.student_usn}</span>
                        </div>
                      </div>
                      <div className="mdh-at-risk-issues">
                        {student.issues.slice(0, 2).map((issue, i) => (
                          <span key={i} className={`mdh-issue-tag mdh-issue-${issue.severity}`}>
                            {issue.message}
                          </span>
                        ))}
                        {student.issues.length > 2 && (
                          <span className="mdh-issue-more">+{student.issues.length - 2} more</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Mini Calendar */}
          <div className="mdh-section-card">
            <div className="mdh-section-header">
              <h3><FaCalendarAlt className="mdh-section-icon" /> Meetings Calendar</h3>
              <div className="mdh-calendar-nav">
                <button onClick={() => setCalendarWeekOffset(prev => prev - 1)}><FaChevronLeft /></button>
                <button onClick={() => setCalendarWeekOffset(0)}>Today</button>
                <button onClick={() => setCalendarWeekOffset(prev => prev + 1)}><FaChevronRight /></button>
              </div>
            </div>
            <div className="mdh-calendar-content">
              <div className="mdh-calendar-grid">
                {weekDays.map((day, idx) => {
                  const dateStr = day.toISOString().split('T')[0];
                  const dayEvents = getEventsForDay(day);
                  const isToday = dateStr === today;
                  
                  return (
                    <div key={idx} className={`mdh-calendar-day ${isToday ? 'mdh-calendar-day--today' : ''}`}>
                      <div className="mdh-calendar-day-header">
                        <span className="mdh-calendar-day-name">{day.toLocaleDateString('en-US', { weekday: 'short' })}</span>
                        <span className="mdh-calendar-day-num">{day.getDate()}</span>
                      </div>
                      <div className="mdh-calendar-day-events">
                        {dayEvents.slice(0, 2).map((event, i) => (
                          <div key={i} className={`mdh-calendar-event mdh-event-${event.status}`}>
                            <span className="mdh-event-time">{event.time}</span>
                            <span className="mdh-event-title">{event.student_name}</span>
                          </div>
                        ))}
                        {dayEvents.length > 2 && (
                          <span className="mdh-calendar-more">+{dayEvents.length - 2} more</span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        <div className="mdh-column">
          {/* Activity Feed */}
          <div className="mdh-section-card mdh-activity-feed-card">
            <div className="mdh-section-header">
              <h3><FaClock className="mdh-section-icon" /> Recent Activity</h3>
            </div>
            <div className="mdh-section-content">
              {activityFeed.length === 0 ? (
                <p className="mdh-empty-text">No recent activity to display.</p>
              ) : (
                <div className="mdh-activity-feed">
                  {activityFeed.slice(0, 8).map((activity, idx) => (
                    <div key={idx} className="mdh-activity-item">
                      <div className="mdh-activity-icon">
                        {activity.type === 'meeting_completed' && <FaCheckCircle className="mdh-icon-success" />}
                        {activity.type === 'form_submitted' && <FaClipboardList className="mdh-icon-info" />}
                        {activity.type === 'activity_submitted' && <FaTasks className="mdh-icon-primary" />}
                        {activity.type === 'swot_generated' && <FaChartPie className="mdh-icon-warning" />}
                      </div>
                      <div className="mdh-activity-content">
                        <strong>{activity.title}</strong>
                        <p>{activity.description}</p>
                        <span className="mdh-activity-time">{activity.time_ago}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Form Completion Table with Search/Filter */}
      <section className="mentor-dashboard-home__forms-section">
        <div className="mentor-dashboard-home__forms-header">
          <div>
            <h2 className="mentor-dashboard-home__forms-title">Mentees - Form completion</h2>
            <p className="mentor-dashboard-home__forms-subtitle">
              Track which mentee has completed each step (signup, profile, forms, SWOT, activities, MCA).
            </p>
          </div>
        </div>
        
        {/* Search and Filter Bar */}
        <div className="mdh-table-controls">
          <div className="mdh-search-box">
            <FaSearch className="mdh-search-icon" />
            <input
              type="text"
              placeholder="Search by USN or Name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          
          <div className="mdh-filter-group">
            <FaFilter className="mdh-filter-icon" />
            <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
              <option value="all">All Students</option>
              <option value="complete">Complete Flow</option>
              <option value="incomplete">Incomplete</option>
              <option value="no_profile">No Profile</option>
            </select>
          </div>
          
          <div className="mdh-sort-group">
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="usn">Sort by USN</option>
              <option value="name">Sort by Name</option>
              <option value="status">Sort by Status</option>
            </select>
            <button 
              className="mdh-sort-order-btn"
              onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
            >
              {sortOrder === 'asc' ? '↑' : '↓'}
            </button>
          </div>
          
          <button className="mdh-export-btn" onClick={handleExportCSV}>
            <FaDownload /> Export CSV
          </button>
        </div>

        {filteredAndSortedRows.length === 0 ? (
          <p className="mentor-dashboard-home__forms-empty">
            {searchQuery || filterStatus !== 'all' 
              ? 'No students match your search/filter criteria.' 
              : 'No assigned students yet. Once students are assigned, their progress will appear here.'}
          </p>
        ) : (
          <div className="mentor-dashboard-home__forms-table-wrapper">
            <table className="mentor-dashboard-home__forms-table">
              <thead>
                <tr>
                  <th>USN</th>
                  <th>Name</th>
                  <th>Signed up</th>
                  <th>Profile</th>
                  <th>Psychometric</th>
                  <th>SWOT</th>
                  <th>Activities</th>
                  <th>MCA Form</th>
                  <th>16PF</th>
                  <th>IBP</th>
                  <th>Overall status</th>
                </tr>
              </thead>
              <tbody>
                {filteredAndSortedRows.map((row) => (
                  <tr key={row.student_usn}>
                    <td>{row.student_usn}</td>
                    <td>{row.student_name || '—'}</td>
                    <td><span className={row.signedUp ? 'mh-badge mh-badge--yes' : 'mh-badge mh-badge--no'}>{row.signedUp ? 'Yes' : 'No'}</span></td>
                    <td><span className={row.profileCreated ? 'mh-badge mh-badge--yes' : 'mh-badge mh-badge--no'}>{row.profileCreated ? 'Yes' : 'No'}</span></td>
                    <td><span className={row.psychometricFilled ? 'mh-badge mh-badge--yes' : 'mh-badge mh-badge--no'}>{row.psychometricFilled ? 'Yes' : 'No'}</span></td>
                    <td><span className={row.swotGenerated ? 'mh-badge mh-badge--yes' : 'mh-badge mh-badge--no'}>{row.swotGenerated ? 'Yes' : 'No'}</span></td>
                    <td><span className={row.activitiesGenerated ? 'mh-badge mh-badge--yes' : 'mh-badge mh-badge--no'}>{row.activitiesGenerated ? 'Yes' : 'No'}</span></td>
                    <td><span className={row.mcaFilled ? 'mh-badge mh-badge--yes' : 'mh-badge mh-badge--no'}>{row.mcaFilled ? 'Yes' : 'No'}</span></td>
                    <td><span className={row.pf16Filled ? 'mh-badge mh-badge--yes' : 'mh-badge mh-badge--no'}>{row.pf16Filled ? 'Yes' : 'No'}</span></td>
                    <td><span className={row.ibpFilled ? 'mh-badge mh-badge--yes' : 'mh-badge mh-badge--no'}>{row.ibpFilled ? 'Yes' : 'No'}</span></td>
                    <td className="mentor-dashboard-home__forms-status-text">{row.statusText}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Email Section */}
      <section className="mdh-email-section-wrapper">
        <div className="mdh-email-compose">
          <div className="mdh-section-header">
            <h3><FaEnvelope className="mdh-section-icon mdh-icon-primary" /> Compose Email</h3>
          </div>
          <div className="mdh-section-content">
            {assignedStudents.length === 0 ? (
              <p className="mdh-empty-text">No assigned students. You cannot send emails until students are assigned to you.</p>
            ) : (
              <form onSubmit={handleSendEmail} className="mdh-email-form">
                <div className="mdh-email-form-group">
                  <label htmlFor="email-student">To</label>
                  <select id="email-student" value={emailStudentUsn} onChange={(e) => setEmailStudentUsn(e.target.value)} required>
                    <option value="">Select a student</option>
                    {assignedStudents.map((s) => (
                      <option key={s.student_usn} value={s.student_usn}>
                        {s.student_name || s.student_usn} ({s.student_usn})
                      </option>
                    ))}
                  </select>
                </div>
                <div className="mdh-email-form-group">
                  <label htmlFor="email-subject">Subject</label>
                  <input id="email-subject" type="text" value={emailSubject} onChange={(e) => setEmailSubject(e.target.value)} placeholder="Enter subject..." required />
                </div>
                <div className="mdh-email-form-group">
                  <label htmlFor="email-message">Message</label>
                  <textarea id="email-message" value={emailMessage} onChange={(e) => setEmailMessage(e.target.value)} placeholder="Write your message here..." rows={5} required />
                </div>
                {emailResult && (
                  <div className={`mdh-email-result ${emailResult.success ? 'mdh-email-result--success' : 'mdh-email-result--error'}`}>
                    {emailResult.success ? <FaCheckCircle /> : <FaExclamationTriangle />}
                    <span>{emailResult.message}</span>
                  </div>
                )}
                <button type="submit" className="mdh-email-send-btn" disabled={emailSending}>
                  {emailSending ? 'Sending...' : <><FaEnvelope /> Send Email</>}
                </button>
              </form>
            )}
          </div>
        </div>

        {/* Email History Section */}
        <div className="mdh-email-history">
          <div className="mdh-section-header">
            <h3><FaClock className="mdh-section-icon" /> Email History</h3>
            <span className="mdh-section-badge mdh-badge-info">{emailHistory.length}</span>
          </div>
          <div className="mdh-section-content mdh-email-history-content">
            {emailHistory.length === 0 ? (
              <div className="mdh-email-empty-state">
                <FaEnvelope className="mdh-email-empty-icon" />
                <p>No emails sent yet</p>
                <span>Your sent emails will appear here</span>
              </div>
            ) : (
              <div className="mdh-email-list">
                {emailHistory.map((email) => (
                  <div 
                    key={email.id} 
                    className={`mdh-email-item ${selectedEmail?.id === email.id ? 'mdh-email-item--selected' : ''}`}
                    onClick={() => setSelectedEmail(selectedEmail?.id === email.id ? null : email)}
                  >
                    <div className="mdh-email-item-header">
                      <div className="mdh-email-recipient">
                        <FaUserGraduate className="mdh-email-avatar" />
                        <div>
                          <strong>{email.recipient_name}</strong>
                          <span className="mdh-email-usn">{email.student_usn}</span>
                        </div>
                      </div>
                      <div className="mdh-email-meta">
                        <span className={`mdh-email-status mdh-email-status--${email.status}`}>
                          {email.status === 'sent' ? <FaCheckCircle /> : <FaExclamationTriangle />}
                        </span>
                        <span className="mdh-email-time">{formatEmailDate(email.sent_at)}</span>
                      </div>
                    </div>
                    <div className="mdh-email-subject">
                      <strong>Subject:</strong> {email.subject}
                    </div>
                    {selectedEmail?.id === email.id && (
                      <div className="mdh-email-body">
                        <div className="mdh-email-body-label">Message:</div>
                        <div className="mdh-email-body-content">{email.full_message}</div>
                        <div className="mdh-email-body-footer">
                          <span>Sent to: {email.recipient_email}</span>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
};

export default MentorDashboardHome;
