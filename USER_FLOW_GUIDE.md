# Mentee Tracker MCA - User Flow Guide

## 📋 Table of Contents
1. [Getting Started](#getting-started)
2. [Student User Journey](#student-user-journey)
3. [Mentor User Journey](#mentor-user-journey)
4. [Administrator User Journey](#administrator-user-journey)
5. [Common User Scenarios](#common-user-scenarios)
6. [Troubleshooting User Issues](#troubleshooting-user-issues)

---

## 🚀 Getting Started

### First Time Access
1. **Open the Application**: Navigate to `http://localhost:3000` (or your deployed URL)
2. **Landing Page**: You'll see the Mentee Tracker MCA welcome page
3. **Choose Your Role**: Click on the appropriate login option:
   - **Student Login** - For students to access their dashboard
   - **Mentor Login** - For mentors to manage their students
   - **Admin Login** - For administrators to manage the system

---

## 👨‍🎓 Student User Journey

### Step 1: Registration & Login

#### New Student Registration:
1. **Click "Student Signup"** on the landing page
2. **Fill Registration Form**:
   - Student USN (University Serial Number)
   - Full Name
   - Email Address
   - Phone Number
   - Password
   - Confirm Password
3. **Submit Registration** - You'll receive a confirmation email
4. **Login** with your credentials

#### Existing Student Login:
1. **Click "Student Login"**
2. **Enter Credentials**:
   - USN or Email
   - Password
3. **Click "Login"** - You'll be redirected to your dashboard

### Step 2: Student Dashboard Overview

Upon login, you'll see your **Student Dashboard** with:

#### Main Navigation:
- **Dashboard** - Overview of your progress
- **Activities** - Manage your mentorship activities
- **Meetings** - Schedule and view meetings with your mentor
- **MCA Assessment** - Complete competency assessments
- **Reports** - View your progress reports
- **Profile** - Manage your personal information
- **Query** - Submit questions to your mentor

#### Dashboard Widgets:
- **Progress Overview** - Visual progress indicators
- **Recent Activities** - Latest submitted activities
- **Upcoming Meetings** - Scheduled mentor meetings
- **Competency Scores** - Your current competency ratings
- **Notifications** - Important updates and reminders

### Step 3: Managing Activities

#### Creating a New Activity:
1. **Navigate to "Activities"** from the main menu
2. **Click "Create New Activity"**
3. **Fill Activity Details**:
   - Activity Title
   - Description
   - Category (Academic, Personal Development, Career Planning, etc.)
   - Start Date
   - Target Completion Date
   - Goals and Objectives
4. **Submit Activity** - It will be sent to your mentor for approval

#### Tracking Activity Progress:
1. **View "My Activities"** list
2. **Click on an Activity** to see details
3. **Update Progress**:
   - Add progress notes
   - Upload supporting documents
   - Mark milestones as completed
4. **Submit Updates** - Your mentor will be notified

#### Activity Statuses:
- **Draft** - Activity created but not submitted
- **Pending Approval** - Submitted to mentor for review
- **Approved** - Mentor approved, you can start working
- **In Progress** - Currently working on the activity
- **Completed** - Activity finished and submitted
- **Approved by Mentor** - Mentor confirmed completion

### Step 4: Meeting Management

#### Requesting a Meeting:
1. **Go to "Meetings"** section
2. **Click "Request Meeting"**
3. **Fill Meeting Details**:
   - Meeting Type (One-on-one, Group, Virtual, In-person)
   - Preferred Date and Time
   - Meeting Duration
   - Agenda/Topics to Discuss
   - Meeting Location (if in-person)
4. **Submit Request** - Your mentor will receive a notification

#### Viewing Meeting History:
1. **Navigate to "Meetings"**
2. **View "Meeting History"** tab
3. **See Past Meetings** with:
   - Meeting date and time
   - Meeting type
   - Discussion topics
   - Action items
   - Meeting notes (if shared by mentor)

### Step 5: MCA Assessment

#### Completing Competency Assessment:
1. **Go to "MCA Assessment"** from the main menu
2. **Select Assessment Type**:
   - Initial Assessment (for new students)
   - Progress Assessment (quarterly/semester)
   - Final Assessment (end of program)
3. **Answer Questions** in each competency area:
   - Communication Skills
   - Leadership Abilities
   - Problem Solving
   - Teamwork
   - Technical Skills
   - Personal Development
4. **Submit Assessment** - AI will generate observations

#### Viewing Assessment Results:
1. **Navigate to "Reports"**
2. **Click "Competency Report"**
3. **View Results**:
   - Radar chart showing competency scores
   - AI-generated observations
   - Recommendations for improvement
   - Comparison with previous assessments

### Step 6: Viewing Reports

#### Progress Reports:
1. **Go to "Reports"** section
2. **Select Report Type**:
   - Activity Progress Report
   - Competency Development Report
   - Meeting Summary Report
   - Overall Progress Report
3. **Choose Date Range**
4. **Generate Report** - View or download PDF

#### Report Features:
- **Visual Charts** - Progress over time
- **Competency Radar** - Skills assessment visualization
- **Activity Timeline** - Chronological activity view
- **Mentor Feedback** - Comments and recommendations

### Step 7: Submitting Queries

#### Asking Questions to Mentor:
1. **Navigate to "Query"** section
2. **Click "New Query"**
3. **Fill Query Form**:
   - Query Category (Academic, Career, Personal, Technical)
   - Subject Line
   - Detailed Question
   - Priority Level (Low, Medium, High, Urgent)
4. **Submit Query** - Your mentor will respond

#### Viewing Query Responses:
1. **Go to "Query"** section
2. **View "My Queries"** list
3. **Click on Query** to see:
   - Your original question
   - Mentor's response
   - Response date
   - Follow-up options

---

## 👨‍🏫 Mentor User Journey

### Step 1: Mentor Login

1. **Click "Mentor Login"** on the landing page
2. **Enter Credentials**:
   - Mentor ID or Email
   - Password
3. **Access Mentor Dashboard**

### Step 2: Mentor Dashboard Overview

#### Main Navigation:
- **Dashboard** - Overview of assigned students
- **Students** - Manage assigned students
- **Activities** - Review and approve student activities
- **Meetings** - Schedule and manage meetings
- **Reports** - Generate student reports
- **Profile** - Manage mentor profile

#### Dashboard Widgets:
- **Assigned Students** - List of your mentees
- **Pending Approvals** - Activities waiting for review
- **Upcoming Meetings** - Scheduled meetings
- **Student Progress** - Overall progress overview
- **Notifications** - Student requests and updates

### Step 3: Managing Assigned Students

#### Viewing Student List:
1. **Navigate to "Students"** section
2. **View Student Cards** showing:
   - Student name and USN
   - Current semester/year
   - Progress percentage
   - Last activity date
   - Overall competency score

#### Accessing Student Details:
1. **Click on Student Card**
2. **View Student Profile**:
   - Personal information
   - Academic details
   - Activity history
   - Meeting history
   - Competency scores
   - Recent submissions

### Step 4: Activity Management

#### Reviewing Student Activities:
1. **Go to "Activities"** section
2. **View "Pending Approvals"** tab
3. **Review Activity Details**:
   - Activity description
   - Student goals
   - Timeline
   - Supporting documents
4. **Take Action**:
   - **Approve** - Activity can proceed
   - **Request Changes** - Send back with feedback
   - **Reject** - Activity not suitable

#### Monitoring Activity Progress:
1. **Navigate to "Activities"**
2. **View "In Progress"** activities
3. **Check Student Updates**:
   - Progress notes
   - Milestone completions
   - Document uploads
4. **Provide Feedback**:
   - Add comments
   - Suggest improvements
   - Approve milestones

### Step 5: Meeting Management

#### Scheduling Meetings:
1. **Go to "Meetings"** section
2. **View "Meeting Requests"** from students
3. **Review Request Details**:
   - Student name
   - Preferred date/time
   - Meeting agenda
   - Meeting type
4. **Schedule Meeting**:
   - Confirm or suggest alternative time
   - Add meeting location
   - Set meeting duration
   - Add agenda items

#### Conducting Meetings:
1. **Navigate to "Meetings"**
2. **View "Today's Meetings"**
3. **Access Meeting Details**:
   - Student information
   - Meeting agenda
   - Previous meeting notes
   - Student's recent activities
4. **Add Meeting Notes** after the meeting:
   - Discussion points
   - Action items
   - Student concerns
   - Next steps

### Step 6: Generating Reports

#### Creating Student Reports:
1. **Navigate to "Reports"** section
2. **Select Student** from dropdown
3. **Choose Report Type**:
   - Progress Report
   - Competency Assessment Report
   - Activity Summary Report
   - Meeting Summary Report
4. **Customize Report**:
   - Date range
   - Include sections
   - Add mentor comments
5. **Generate Report** - View or download PDF

#### Report Features:
- **Student Progress Overview**
- **Activity Completion Status**
- **Competency Development**
- **Meeting History**
- **Mentor Recommendations**
- **Future Goals**

---

## 👨‍💼 Administrator User Journey

### Step 1: Admin Login

1. **Click "Admin Login"** on the landing page
2. **Enter Admin Credentials**:
   - Admin ID
   - Password
3. **Access Admin Dashboard**

### Step 2: Admin Dashboard Overview

#### Main Navigation:
- **Dashboard** - System overview
- **Students** - Manage all students
- **Mentors** - Manage all mentors
- **Activities** - Configure system activities
- **Analytics** - System-wide analytics
- **Settings** - System configuration

#### Dashboard Widgets:
- **Total Users** - Students, mentors, admins count
- **Active Activities** - Currently active activities
- **System Health** - Database and service status
- **Recent Activity** - Latest system activities
- **Performance Metrics** - Usage statistics

### Step 3: User Management

#### Managing Students:
1. **Navigate to "Students"** section
2. **View Student List** with:
   - Student details
   - Assigned mentor
   - Activity status
   - Last login
3. **Student Actions**:
   - **Add New Student** - Create student account
   - **Edit Student** - Update information
   - **Assign Mentor** - Link student to mentor
   - **View Progress** - Access student reports
   - **Deactivate** - Disable student account

#### Managing Mentors:
1. **Go to "Mentors"** section
2. **View Mentor List** with:
   - Mentor details
   - Assigned students count
   - Activity approvals
   - Performance metrics
3. **Mentor Actions**:
   - **Add New Mentor** - Create mentor account
   - **Edit Mentor** - Update information
   - **Assign Students** - Link students to mentor
   - **View Performance** - Access mentor reports
   - **Manage Permissions** - Set access levels

### Step 4: Activity Configuration

#### Creating System Activities:
1. **Navigate to "Activities"** section
2. **Click "Create Activity Template"**
3. **Define Activity**:
   - Activity name and description
   - Category and type
   - Required fields
   - Approval workflow
   - Completion criteria
4. **Save Template** - Available for mentors to assign

#### Managing Activity Categories:
1. **Go to "Activity Categories"**
2. **View/Edit Categories**:
   - Academic Development
   - Personal Growth
   - Career Planning
   - Technical Skills
   - Leadership Development
3. **Configure Category Settings**:
   - Required competencies
   - Approval process
   - Documentation requirements

### Step 5: System Analytics

#### Viewing System Reports:
1. **Navigate to "Analytics"** section
2. **Select Report Type**:
   - User Engagement Report
   - Activity Completion Report
   - Mentor Performance Report
   - System Usage Report
3. **Customize Report**:
   - Date range
   - User groups
   - Metrics to include
4. **Generate Report** - Export data for analysis

#### Key Metrics:
- **User Activity** - Login frequency, feature usage
- **Activity Completion** - Success rates, time to completion
- **Mentor Performance** - Response times, student satisfaction
- **System Performance** - Response times, error rates

---

## 🔄 Common User Scenarios

### Scenario 1: Student Completing First Activity

1. **Student logs in** for the first time
2. **Views dashboard** and sees welcome message
3. **Navigates to Activities** section
4. **Creates new activity** with goals and timeline
5. **Submits for mentor approval**
6. **Receives notification** when mentor approves
7. **Starts working** on the activity
8. **Updates progress** regularly
9. **Submits completion** with supporting documents
10. **Receives final approval** from mentor

### Scenario 2: Mentor Reviewing Student Progress

1. **Mentor logs in** and sees pending approvals
2. **Reviews student activity** submission
3. **Provides feedback** and approves/rejects
4. **Schedules meeting** to discuss progress
5. **Conducts meeting** and takes notes
6. **Generates progress report** for student
7. **Sets goals** for next period

### Scenario 3: Administrator Managing System

1. **Admin logs in** and reviews system health
2. **Checks new student registrations**
3. **Assigns students** to appropriate mentors
4. **Reviews system analytics** for performance
5. **Configures new activities** for the semester
6. **Generates institutional reports**

### Scenario 4: MCA Assessment Process

1. **Student receives notification** to complete assessment
2. **Accesses MCA Assessment** section
3. **Completes questionnaire** in all competency areas
4. **Submits assessment** for processing
5. **AI generates observations** and recommendations
6. **Student views results** with radar chart
7. **Mentor reviews results** and provides feedback
8. **Both discuss** development plan based on results

---

## 🆘 Troubleshooting User Issues

### Common Student Issues:

#### "I can't log in"
- **Check credentials** - Ensure USN/email and password are correct
- **Reset password** - Use "Forgot Password" link
- **Contact admin** - If account is locked or doesn't exist

#### "My activity is stuck in pending"
- **Check mentor availability** - Mentor might be on leave
- **Contact mentor directly** - Send a query or email
- **Contact admin** - If mentor is unresponsive

#### "I can't see my reports"
- **Complete MCA assessment** - Reports require assessment data
- **Check date range** - Ensure you're looking at the right period
- **Contact support** - If reports are missing

### Common Mentor Issues:

#### "I can't see my assigned students"
- **Check admin assignment** - Ensure students are properly assigned
- **Refresh dashboard** - Try logging out and back in
- **Contact admin** - If assignment is incorrect

#### "Student activity is not showing"
- **Check activity status** - Student might not have submitted
- **Verify student access** - Ensure student account is active
- **Check filters** - Make sure you're viewing all statuses

### Common Admin Issues:

#### "System is running slowly"
- **Check database connection** - Verify MySQL is running
- **Monitor server resources** - Check CPU and memory usage
- **Review error logs** - Look for application errors

#### "Users can't access features"
- **Check permissions** - Verify role-based access is working
- **Test authentication** - Ensure JWT tokens are valid
- **Review system logs** - Look for authentication errors

---

## 📱 Mobile Usage Tips

### Responsive Design Features:
- **Touch-friendly interface** - All buttons and forms are mobile-optimized
- **Swipe navigation** - Easy navigation between sections
- **Mobile forms** - Optimized input fields for mobile devices
- **Offline capability** - Some features work without internet connection

### Best Practices:
- **Use landscape mode** for reports and charts
- **Enable notifications** for important updates
- **Bookmark frequently used pages**
- **Use voice input** for long text entries

---

## 🎯 Success Tips for Users

### For Students:
- **Set realistic goals** in your activities
- **Update progress regularly** to keep mentor informed
- **Ask questions** when you need help
- **Complete assessments honestly** for accurate feedback
- **Review reports** to track your development

### For Mentors:
- **Respond promptly** to student requests
- **Provide constructive feedback** on activities
- **Schedule regular meetings** with students
- **Use reports** to track student progress
- **Communicate clearly** about expectations

### For Administrators:
- **Monitor system health** regularly
- **Keep user data updated** and accurate
- **Configure activities** that align with institutional goals
- **Review analytics** to improve the system
- **Provide training** to new users

---

*This user flow guide provides step-by-step instructions for using the Mentee Tracker MCA application. Each user role has specific workflows and features designed to support effective mentorship relationships and academic development.*
