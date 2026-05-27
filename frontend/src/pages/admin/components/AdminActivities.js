import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import '../../../assets/css/AdminActivities.css';
import { API_BASE_URL } from '../../../api';
import * as XLSX from 'xlsx';

const AdminActivities = () => {
    const { admin_id } = useParams();
    const [activities, setActivities] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [selectedMentor, setSelectedMentor] = useState('');
    const [selectedDepartment, setSelectedDepartment] = useState('');

    useEffect(() => {
        fetch(`${API_BASE_URL}/admin/${admin_id}/activities`)
            .then((response) => {
                if (!response.ok) {
                    throw new Error('Activities not found');
                }
                return response.json();
            })
            .then((data) => {
                const flattenedActivities = data.activities.flat();
                setActivities(flattenedActivities);
                setIsLoading(false);
            })
            .catch((error) => {
                console.error('Error fetching activities:', error);
                setIsLoading(false);
            });
    }, [admin_id]);

    // Get unique departments
    const uniqueDepartments = [...new Set(activities.map((act) => act.student_program))];

    // Filter mentors based on selected department
    const mentorsInSelectedDepartment = activities
        .filter((act) => selectedDepartment ? act.student_program === selectedDepartment : true)
        .map((act) => act.assigned_mentor);
    
    const uniqueMentors = [...new Set(mentorsInSelectedDepartment)];

    // Filter activities
    const filteredActivities = activities.filter((activity) =>
        (selectedDepartment ? activity.student_program === selectedDepartment : true) &&
        (selectedMentor ? activity.assigned_mentor === selectedMentor : true)
    );

    const downloadExcel = () => {
        const data = filteredActivities.map((activity) => ({
            'Student USN': activity.student_usn,
            'Student Name': activity.student_name,
            'Student Program': activity.student_program,
            'Assigned Mentor': activity.assigned_mentor,
            Activity: activity.activity,
            Duration: activity.duration_type,
            'Generated At': new Date(activity.generated_at).toLocaleString(),
        }));

        const ws = XLSX.utils.json_to_sheet(data);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, 'Filtered Activities');
        XLSX.writeFile(wb, 'filtered_activities.xlsx');
    };

    if (isLoading) {
        return <div>Loading...</div>;
    }

    return (
        <div className="admin-activities__content">
            <h2 className="admin-activities__title">Student Activities</h2>

            {/* Filters */}
            <div className="admin-students__filters">
                {/* Department Dropdown (First) */}
                <select value={selectedDepartment} onChange={(e) => {
                    setSelectedDepartment(e.target.value);
                    setSelectedMentor(''); // Reset mentor when department changes
                }}>
                    <option value="">All Departments</option>
                    {uniqueDepartments.map((dept, index) => (
                        <option key={index} value={dept}>
                            {dept}
                        </option>
                    ))}
                </select>

                {/* Mentor Dropdown (Filtered by Department) */}
                <select value={selectedMentor} onChange={(e) => setSelectedMentor(e.target.value)}>
                    <option value="">All Mentors</option>
                    {uniqueMentors.map((mentor, index) => (
                        <option key={index} value={mentor}>
                            {mentor}
                        </option>
                    ))}
                </select>
            </div>

            {/* Download Button */}
            <button className="download-excel-btn" onClick={downloadExcel}>
                Download as Excel
            </button>

            {filteredActivities.length > 0 ? (
                <div className="admin-activities__table-container">
                    <table className="admin-activities__table">
                        <thead>
                            <tr>
                                <th>Student USN</th>
                                <th>Student Name</th>
                                <th>Student Program</th>
                                <th>Assigned Mentor</th>
                                <th>Activity</th>
                                <th>Duration</th>
                                <th>Generated At</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredActivities.map((activity, index) => (
                                <tr key={index}>
                                    <td>{activity.student_usn}</td>
                                    <td>{activity.student_name}</td>
                                    <td>{activity.student_program}</td>
                                    <td>{activity.assigned_mentor}</td>
                                    <td>{activity.activity}</td>
                                    <td>{activity.duration_type}</td>
                                    <td>{new Date(activity.generated_at).toLocaleString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            ) : (
                <div className="admin-activities__no-activities">
                    <p>No activities found.</p>
                </div>
            )}
        </div>
    );
};

export default AdminActivities;
