-- =====================================================
-- SQL Queries: Students Assigned to Mentors by Department
-- =====================================================

-- Query 1: Count students assigned to each mentor, grouped by department
-- Shows all mentors with their student counts, organized by department
SELECT 
    m.mentor_department AS department,
    m.mentor_id,
    m.mentor_name,
    COUNT(s.student_usn) AS student_count
FROM 
    mentors m
LEFT JOIN 
    students s ON m.mentor_id = s.assigned_mentor
GROUP BY 
    m.mentor_department, m.mentor_id, m.mentor_name
ORDER BY 
    m.mentor_department, student_count DESC;

-- Query 2: Department-wise summary (total students per department)
-- Shows total number of students assigned to mentors in each department
SELECT 
    m.mentor_department AS department,
    COUNT(DISTINCT m.mentor_id) AS total_mentors,
    COUNT(s.student_usn) AS total_students
FROM 
    mentors m
LEFT JOIN 
    students s ON m.mentor_id = s.assigned_mentor
GROUP BY 
    m.mentor_department
ORDER BY 
    total_students DESC;

-- Query 3: For a specific mentor (replace 'MENTOR_ID' with actual mentor_id)
-- Shows student count for a particular mentor
SELECT 
    m.mentor_department AS department,
    m.mentor_id,
    m.mentor_name,
    COUNT(s.student_usn) AS student_count
FROM 
    mentors m
LEFT JOIN 
    students s ON m.mentor_id = s.assigned_mentor
WHERE 
    m.mentor_id = 'MENTOR_ID'  -- Replace with actual mentor_id
GROUP BY 
    m.mentor_department, m.mentor_id, m.mentor_name;

-- Query 4: Detailed view - List all students assigned to mentors by department
-- Shows actual student details along with their mentor's department
SELECT 
    m.mentor_department AS department,
    m.mentor_id,
    m.mentor_name AS mentor_name,
    s.student_usn,
    s.student_name,
    s.student_program,
    s.semester
FROM 
    mentors m
INNER JOIN 
    students s ON m.mentor_id = s.assigned_mentor
ORDER BY 
    m.mentor_department, m.mentor_name, s.student_usn;

-- Query 5: Mentors with no students assigned (by department)
-- Shows mentors who don't have any students assigned
SELECT 
    m.mentor_department AS department,
    m.mentor_id,
    m.mentor_name,
    0 AS student_count
FROM 
    mentors m
LEFT JOIN 
    students s ON m.mentor_id = s.assigned_mentor
WHERE 
    s.assigned_mentor IS NULL
GROUP BY 
    m.mentor_department, m.mentor_id, m.mentor_name
ORDER BY 
    m.mentor_department, m.mentor_name;
