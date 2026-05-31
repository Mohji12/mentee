from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.students import Student
from app.db.models.mentors import Mentor
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from fastapi.responses import StreamingResponse
from app.db.models.competencies import Competencies
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from app.utils.competencies_rating import get_competency_rating
from app.utils.radar import create_radar_chart
from reportlab.lib.utils import ImageReader
from app.db.models.mentee_competency_report import MenteeCompetencyReport
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.units import cm
from sqlalchemy import func
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

router = APIRouter()

# Module-level cache for S3 images (avoids re-downloading on every report)
_IMAGE_CACHE = {}
IMAGE_URLS = {
    "watermark": "https://res.cloudinary.com/dvlitilou/image/upload/v1779924616/Screenshot_2025-06-30_140404-removebg-preview_jcrpar.png",
    "jain_logo": "https://res.cloudinary.com/dvlitilou/image/upload/v1779924616/Jain-Logo_jix84i.png",
    "mentee_logo": "https://res.cloudinary.com/dvlitilou/image/upload/v1779924617/logo_mentee-removebg-preview_coyhds.png",
}


def _get_all_report_images():
    """Fetch all report images in parallel; return (watermark_buf, jain_reader, mentee_reader). Buffers are reused; readers are from cached bytes."""
    session = requests.Session()
    results = {}

    def get_one(key):
        url = IMAGE_URLS[key]
        if url in _IMAGE_CACHE:
            buf = _IMAGE_CACHE[url]
            buf.seek(0)
            return key, BytesIO(buf.getvalue())
        try:
            r = session.get(url, timeout=10)
            if r.status_code == 200:
                buf = BytesIO(r.content)
                _IMAGE_CACHE[url] = buf
                return key, buf
        except Exception as e:
            print(f"Failed to fetch {key}: {e}")
        return key, None

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(get_one, k): k for k in IMAGE_URLS}
        for future in as_completed(futures):
            key, buf = future.result()
            results[key] = buf
    # Return watermark as buffer (new reader per page); logos as readers (used once)
    w = results.get("watermark")
    j = results.get("jain_logo")
    m = results.get("mentee_logo")
    return w, ImageReader(j) if j else None, ImageReader(m) if m else None


def add_watermark_to_page(canvas_obj, width, height, watermark_buf=None):
    """Add watermark to a page. watermark_buf is BytesIO (reused across pages via fresh reader per draw)."""
    if watermark_buf is None:
        return
    try:
        buf = BytesIO(watermark_buf.getvalue())
        buf.seek(0)
        reader = ImageReader(buf)
        watermark_width = 400
        watermark_height = 300
        watermark_x = (width - watermark_width) / 2
        watermark_y = (height - watermark_height) / 2
        canvas_obj.saveState()
        canvas_obj.setFillAlpha(0.05)
        canvas_obj.drawImage(reader, watermark_x, watermark_y, width=watermark_width, height=watermark_height)
        canvas_obj.restoreState()
    except Exception as e:
        print(f"Failed to draw watermark: {e}")

@router.get("/reportdownload", response_class=StreamingResponse)
def generate_student_profile_pdf(student_usn: str, db: Session = Depends(get_db)):
    try:
        # Fetch student data
        student = db.query(Student).filter_by(student_usn=student_usn.strip()).first()
        if not student:
            raise HTTPException(status_code=404, detail=f"Student with USN {student_usn} not found")

        # Fetch mentor name if assigned
        mentor_name = None
        if student.assigned_mentor:
            mentor = db.query(Mentor).filter_by(mentor_id=student.assigned_mentor).first()
            if mentor:
                mentor_name = mentor.mentor_name

        # Fetch and calculate competency scores
        COMPETENCY_COLUMNS = [
            "Active_Listening",
            "Building_Trust",
            "Encouraging",
            "Identifying_Goals_Current_Reality",
            "Instructing_Developing_Capabilities",
            "Inspiring",
            "Providing_Corrective_Feedback",
            "Managing_Risks",
            "Opening_Doors"
        ]

        competencies = db.query(Competencies).filter(Competencies.student_usn == student_usn.strip()).first()
        if not competencies:
            raise HTTPException(
                status_code=404, 
                detail="Competency scores not found. Please complete the MCA assessment first to generate the report."
            )

        competency_scores = {
            col: getattr(competencies, col)
            for col in COMPETENCY_COLUMNS
        }

        total_score = sum(score for score in competency_scores.values() if isinstance(score, (int, float)))
        average_score = total_score / len(COMPETENCY_COLUMNS)
        percentage_score = (total_score / (len(COMPETENCY_COLUMNS) * 35)) * 100  # Assuming each score is out of 35

        highest_comp = max(competency_scores, key=competency_scores.get)
        lowest_comp = min(competency_scores, key=competency_scores.get)

        # Rating
        if 30 <= average_score <= 35:
            rating = "Excellent mentor skills; you could coach others; concentrate improvement efforts on fine-tuning your style with particular mentees"
        elif 25 <= average_score <= 29:
            rating = "Very good skills; continue to polish those skills that will make you even more effective and desirable as a mentor"
        elif 15 <= average_score <= 24:
            rating = "Good skills; you need to work on certain areas of improvement to ensure you are an effective and desirable mentor"
        elif 10 <= average_score <= 14:
            rating = "Adequate mentor skills; work on your less-developed skills in order to acquire strong mentees and have better relationships with them"
        else:  # 9 or under
            rating = "You will benefit from coaching and practice on mentor skills; acquire training or coaching, and observe others who have strong skill"

        # Fetch all report images once (parallel, cached for subsequent requests)
        watermark_reader, jain_logo_reader, mentee_logo_reader = _get_all_report_images()

        # Create PDF in memory
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        width, height = A4

        # Add Jain Logo to the top left corner of the first page (pre-fetched)
        if jain_logo_reader:
            try:
                jain_logo_width, jain_logo_height = 120, 60
                jain_logo_x = 30
                jain_logo_y = height - jain_logo_height - 30
                c.drawImage(jain_logo_reader, jain_logo_x, jain_logo_y, width=jain_logo_width, height=jain_logo_height)
            except Exception as e:
                print(f"Failed to draw Jain logo: {e}")

        # Add Mentee Tracker Logo to the top right corner (pre-fetched)
        if mentee_logo_reader:
            try:
                mentee_logo_width, mentee_logo_height = 120, 60
                mentee_logo_x = width - mentee_logo_width - 30
                mentee_logo_y = height - mentee_logo_height - 30
                c.drawImage(mentee_logo_reader, mentee_logo_x, mentee_logo_y, width=mentee_logo_width, height=mentee_logo_height)
            except Exception as e:
                print(f"Failed to draw Mentee Tracker logo: {e}")

        # Add watermark to the first page (pre-fetched, no extra network call)
        add_watermark_to_page(c, width, height, watermark_reader)

        # Report heading
        c.setFont("Helvetica-Bold", 16)
        text = "MCA Report"
        text_width = c.stringWidth(text, "Helvetica-Bold", 16)
        y_position = height - 60
        c.drawString((width - text_width) / 2, y_position, text)

        # Section: Student Details
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 100, "Student Details")
        c.setFont("Helvetica", 12)
        y = height - 130
        line_height = 20

        # List of fields to display (excluding password)
        dob_str = student.date_of_birth.isoformat() if student.date_of_birth else ""
        fields = [
            ("USN", student.student_usn),
            ("Name", student.student_name),
            ("Email", student.student_email),
            ("Phone Number", student.student_phoneno),
            ("Program", student.student_program),
            ("Semester", student.semester),
            ("Batch", student.student_batch),
            ("Assigned Mentor", mentor_name if mentor_name else ""),
            ("LinkedIn", student.linkedin),
            ("Gender", student.gender or ""),
            ("Blood Group", student.blood_group or ""),
            ("Date of Birth", dob_str),
            ("Guardian Contact", student.parent_guardian_contact or ""),
        ]

        for label, value in fields:
            c.drawString(60, y, f"{label}: {value if value is not None else ''}")
            y -= line_height
            if y < 60:
                c.showPage()
                y = height - 60
                c.setFont("Helvetica", 12)

        # Section 2: Report Overview
        y -= 30
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "2. Report Overview")
        y -= 40

        # Style for paragraph wrapping
        styles = getSampleStyleSheet()
        styleN = styles["BodyText"]

        # Prepare table data with wrapped text for rating
        table_data = [
            ["Metric", "Value"],
            ["Total Score", str(total_score)],
            ["Average Score", f"{average_score:.2f}"],
            ["Percentage", f"{percentage_score:.2f}%"],
            ["Highest Competency", f"{highest_comp.replace('_', ' ')} ({competency_scores[highest_comp]})"],
            ["Lowest Competency", f"{lowest_comp.replace('_', ' ')} ({competency_scores[lowest_comp]})"],
            ["Rating", Paragraph(rating, styleN)]  # Wrap long text
        ]

        # Create the table with custom column widths
        table = Table(table_data, colWidths=[250, 250])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        # Adjust Y position if needed to avoid overflow
        table.wrapOn(c, 50, y)
        table.drawOn(c, 50, y - table._height)

        y -= table._height + 20  # Adjust Y position for next section

        # Prepare table data
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "3.1 Competency Scores")

        comp_table_data = [["Competency", "Score", "Score Out of 7"]]
        for comp, score in competency_scores.items():
           avg = round(score / 5, 2)
           comp_table_data.append([comp.replace("_", " "), score, avg])

        # Create table
        comp_table = Table(comp_table_data, colWidths=[220, 100, 130])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        # Estimate and draw table
        comp_table_height = 20 * len(comp_table_data)  # Approx row height * number of rows
        comp_table.wrapOn(c, 50, y - comp_table_height)
        comp_table.drawOn(c, 50, y - comp_table_height)
        y -= comp_table_height + 30  # Update y for next section  

        # Reset Y position for new page
        c.showPage()  # Start a new page
        add_watermark_to_page(c, width, height, watermark_reader)
        y = 750  # Start near the top
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "3.2 Competency-wise Rating")
        y -= 25

        # Prepare second table data
        rating_table_data = [["Competency", "Score", "Rating Description"]]
        for comp, score in competency_scores.items():
          rating_description = get_competency_rating(score)
          rating_table_data.append([
            comp.replace("_", " "),
            score,
            Paragraph(rating_description, styleN)
        ])

        # Create table with wrapped description
        rating_table = Table(rating_table_data, colWidths=[170, 50, 310])
        rating_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
]))

        # Wrap and draw the table
        table_width, table_height = rating_table.wrap(0, 0)
        rating_table.drawOn(c, 50, y - table_height)
        y -= table_height + 30  # Move y below the table + some spacing

        # Draw radar chart below the table (generate once, reuse)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "3.3 Radar Chart of Competencies")
        y -= 30  # Space after heading

        # Matplotlib Agg backend (fast); avoids Plotly/Kaleido hangs on Windows
        radar_buffer = create_radar_chart(competency_scores)
        chart_y = y - 350
        try:
            if radar_buffer and len(radar_buffer.getvalue()) > 0:
                radar_buffer.seek(0)
                chart_image = ImageReader(radar_buffer)
                c.drawImage(chart_image, 100, chart_y, width=350, height=350)
            else:
                c.setFont("Helvetica", 10)
                c.drawString(50, chart_y + 150, "(Radar chart unavailable — report continues below.)")
        except Exception as chart_err:
            print(f"Radar chart omitted from PDF: {chart_err}")
            c.setFont("Helvetica", 10)
            c.drawString(50, chart_y + 150, "(Radar chart unavailable — report continues below.)")

        # Update y position to be below the chart
        y = chart_y - 20  # Space below the chart

        # Section: Competency % Difference
        c.showPage()  # Start a new page
        add_watermark_to_page(c, width, height, watermark_reader)
        y = 750
        y -= 30  # Add spacing below radar chart
        
        # Set the font and draw the "Competency Percentage Differences" section
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "3.4 Competency Percentage Differences")
        y -= 20  # space after the title

        # Calculate % difference from ideal score (35)
        percent_diff_data = [["Competency", "Score", "Max Score", "Percentage", "% Difference from Max"]]
        for comp, score in competency_scores.items():
            percentage = (score / 35) * 100
            diff = 100 - percentage
            percent_diff_data.append([
               comp.replace("_", " "),
               score,
               35,
               f"{percentage:.2f}%",
               f"{diff:.2f}%"
            ])
         
        # Create and style the table
        percent_diff_table = Table(percent_diff_data, colWidths=[170, 60, 60, 100, 130])
        percent_diff_table.setStyle(TableStyle([
          ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
          ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
          ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
          ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
          ('FONTSIZE', (0, 0), (-1, -1), 10),
          ('BACKGROUND', (0, 1), (-1, -1), colors.aliceblue),
          ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
          ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        # Draw the table
        table_width, table_height = percent_diff_table.wrap(0, 0)
        percent_diff_table.drawOn(c, 50, y - table_height)
        y -= table_height + 30  # Adjust space after table
        # Ensure the next section starts below the table
        y -= 20  # Add extra space before starting the detailed report

        # Title for Detailed Report
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "4. Detailed Report")
        y -= 30  # Space after the title

        # Fetch only the latest observation for each competency for the student
        subq = db.query(
            MenteeCompetencyReport.competency,
            func.max(MenteeCompetencyReport.id).label("max_id")
        ).filter(
            MenteeCompetencyReport.student_usn == student_usn
        ).group_by(MenteeCompetencyReport.competency).subquery()

        observations = db.query(MenteeCompetencyReport).join(
            subq,
            (MenteeCompetencyReport.competency == subq.c.competency) & (MenteeCompetencyReport.id == subq.c.max_id)
        ).all()

        # Set font for detailed report
        for obs in observations:
            content = [
                ("Competency:", obs.competency or ""),
                ("Observation:", obs.observation or ""),
                ("Mentor Implication:", obs.mentor_implication or ""),
                ("Recommendation:", obs.recommendation or "")
            ]
            max_line_width = 0  # Initialize it here for each competency block

            for label, detail in content:
               # Handle new page
                if y < 100:
                    c.showPage()
                    add_watermark_to_page(c, width, height, watermark_reader)
                    y = height - 80  # Leave space at top
                    c.setFont("Helvetica", 10)

                # Draw label
                c.setFont("Helvetica-Bold", 12)
                c.drawString(60, y, label)
                y -= 0.5 * cm  # 0.5 cm space (~14 points)

                # Draw wrapped detail
                c.setFont("Helvetica", 10)
                text_lines = []
                while len(detail) > 110:
                    split_point = detail[:110].rfind(' ')
                    if split_point == -1:
                        split_point = 110
                    text_lines.append(detail[:split_point])
                    detail = detail[split_point:].lstrip()
                text_lines.append(detail)
                for txt in text_lines:
                    if y < 60:
                        c.showPage()
                        add_watermark_to_page(c, width, height, watermark_reader)
                        y = height - 80
                        c.setFont("Helvetica", 10)
                        y = height - 50
                    c.drawString(60, y, txt)
                    text_width = stringWidth(txt, "Helvetica", 10)
                    if text_width > max_line_width:
                       max_line_width = text_width

                    y -= 15
                y -= 10   
            c.setLineWidth(1.2)  # Bold line
            c.line(60, y, 60 + max_line_width, y) 
            y -= 20  # space between competencies

        c.save()
        pdf_buffer.seek(0)

        # Get the PDF content length
        pdf_content = pdf_buffer.getvalue()
        content_length = len(pdf_content)

        # Create a new BytesIO from the content to ensure proper streaming
        pdf_stream = BytesIO(pdf_content)
        pdf_stream.seek(0)

        return StreamingResponse(
            pdf_stream, 
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=student_profile_{student_usn}.pdf",
                "Content-Type": "application/pdf",
                "Content-Length": str(content_length),
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like 404 for missing data)
        raise
    except Exception as e:
        # Catch any other errors during PDF generation
        import traceback
        error_details = traceback.format_exc()
        print(f"Error generating PDF for student {student_usn}: {error_details}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating PDF report: {str(e)}. Please try again later or contact support."
        )
