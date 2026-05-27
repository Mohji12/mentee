"""
Export mentee-tracker analytics: table counts, breakdowns, and short insight text to Excel.

Run from project root:
  python export_analytics_excel.py

Optional:
  set OUTPUT_PATH=my_report.xlsx
  set DATABASE_URL=mysql+pymysql://...

Output default: analytics_report_YYYYMMDD_HHMMSS.xlsx

Department buckets use the assigned mentor's mentor_department (students without a mentor
appear as "(no mentor assigned)"). Meetings and counseling use the session mentor's department.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))


def _mask_db_url(url: str) -> str:
    if not url or url.startswith("("):
        return url
    try:
        p = urlparse(url.replace("mysql+pymysql", "mysql", 1))
        if p.hostname:
            return f"{p.scheme or 'mysql'}://***@{p.hostname}{':' + str(p.port) if p.port else ''}{p.path or ''}"
    except Exception:
        pass
    return "(configured)"


def _safe_scalar(db, sql: str, params: dict | None = None) -> Any | None:
    from sqlalchemy import text

    try:
        if params:
            return db.execute(text(sql), params).scalar()
        return db.execute(text(sql)).scalar()
    except Exception:
        return None


def _safe_frame(db, sql: str, columns: list[str]):
    import pandas as pd
    from sqlalchemy import text

    try:
        rows = db.execute(text(sql)).fetchall()
        return pd.DataFrame(rows, columns=columns)
    except Exception as e:
        return pd.DataFrame([{"error": str(e)}])


def _sql_student_department_expr(alias_student: str = "s", alias_mentor: str = "m") -> str:
    """Bucket each student by their mentor's department (same label everywhere)."""
    return f"""CASE
      WHEN {alias_student}.assigned_mentor IS NULL OR TRIM({alias_student}.assigned_mentor) = ''
        THEN '(no mentor assigned)'
      ELSE COALESCE(NULLIF(TRIM({alias_mentor}.mentor_department), ''), '(mentor dept blank)')
    END"""


def _sql_mentor_department_expr(alias_mentor: str = "m") -> str:
    """Department label for a row that already joins mentors."""
    return f"""COALESCE(NULLIF(TRIM({alias_mentor}.mentor_department), ''), '(mentor dept blank)')"""


def _add_department_insights(df: Any, total_students: int) -> Any:
    """Add analytics_insight column to a department-level summary DataFrame."""
    import pandas as pd

    if df is None or df.empty or "error" in df.columns:
        return df
    out = df.copy()
    if "student_count" not in out.columns:
        return out

    sc = out["student_count"].fillna(0).astype(float)
    max_sc = float(sc.max()) if len(sc) else 0.0
    insights: list[str] = []
    for _, row in out.iterrows():
        dept = str(row.get("department", ""))
        stc = int(row.get("student_count") or 0)
        mc = int(row.get("mentor_count") or 0)
        spm = row.get("students_per_mentor")
        pct = (100.0 * stc / total_students) if total_students else 0.0
        parts: list[str] = []
        if dept == "(no mentor assigned)" and stc > 0:
            parts.append("Students not yet linked to any mentor; prioritize allocation.")
        elif float(stc) == max_sc and max_sc > 0 and dept != "(no mentor assigned)":
            parts.append("Largest mentee cohort by assigned mentor department.")
        if mc > 0 and spm is not None and not (isinstance(spm, float) and pd.isna(spm)):
            spm_f = float(spm)
            if spm_f > 18:
                parts.append("High average mentees per mentor — consider rebalancing workload.")
            elif spm_f > 0 and spm_f < 4:
                parts.append("Relatively low mentee load per mentor here.")
        if pct >= 35 and total_students:
            parts.append(f"~{pct:.0f}% of all students sit in this department bucket.")
        if not parts:
            parts.append("Mentor-department view of assigned students and workload.")
        insights.append(" ".join(parts))
    out["analytics_insight"] = insights
    return out


def table_counts(db) -> list[tuple[str, int | str]]:
    """Row counts for known application tables (skips missing tables)."""
    tables = [
        "students",
        "mentors",
        "admin",
        "login",
        "activities",
        "activities_tracking",
        "activity_submissions",
        "meetings",
        "mentoring_assessments",
        "psychometric_responses",
        "mentee_competency_report",
        "swot",
        "competencies",
        "report",
        "query",
        "counseling_sessions",
        "counseling_availability",
        "session_issues_resolutions",
        "counseling_issue_resolution_feedback",
        "counseling_escalations",
        "counseling_reminders",
        "attendance_sessions",
        "attendance",
        "committee_members",
        "pf16_responses",
        "ibp_responses",
        "experience_learning",
        "email_logs",
        "internal_marks_import_batch",
        "internal_marks_entry",
        "academic_performance_lock",
        "academic_performance",
        "academic_performance_marksheets",
        "student_secondary_marksheets",
        "forgot_password",
    ]
    out: list[tuple[str, int | str]] = []
    for t in tables:
        n = _safe_scalar(db, f"SELECT COUNT(*) FROM `{t}`")
        if n is None:
            out.append((t, "n/a (missing or error)"))
        else:
            out.append((t, int(n)))
    return out


def build_insights(
    totals: dict[str, int | None],
) -> list[tuple[str, str, str]]:
    """Turn key numbers into (Metric, Value, Insight) rows."""
    rows: list[tuple[str, str, str]] = []
    students = totals.get("students") or 0
    mentors = totals.get("mentors") or 0
    unassigned = totals.get("students_unassigned") or 0
    assigned = max(students - unassigned, 0)

    rows.append(("Total students", str(students), "Headcount of registered students."))
    rows.append(("Total mentors", str(mentors), "Active mentor accounts in the system."))
    rows.append(
        ("Students with mentor", str(assigned), "Students with assigned_mentor set.")
    )
    rows.append(("Students without mentor", str(unassigned), "May need mentor allocation."))

    if students and mentors:
        ratio = students / mentors
        rows.append(
            (
                "Students per mentor (avg)",
                f"{ratio:.2f}",
                "Rough load if work were evenly split; actual load varies by department.",
            )
        )
    if students:
        pct = 100.0 * unassigned / students
        rows.append(
            (
                "% students unassigned",
                f"{pct:.1f}%",
                "Higher values suggest backlog in mentor assignment.",
            )
        )

    # Activity tracking
    at_total = totals.get("activities_tracking_total") or 0
    for status in ("Approved", "Pending", "Rejected"):
        c = totals.get(f"activities_{status.lower()}") or 0
        label = f"Activities — {status}"
        if at_total:
            pct = 100.0 * c / at_total
            insight = f"{pct:.1f}% of tracked activity rows."
        else:
            insight = "No activity tracking rows."
        rows.append((label, str(c), insight))

    # Meetings
    mt = totals.get("meetings_total") or 0
    rows.append(("Meetings (all)", str(mt), "Scheduled or recorded mentor–student meetings."))
    if mt:
        for st in ("completed", "scheduled", "cancelled"):
            c = totals.get(f"meetings_{st}") or 0
            pct = 100.0 * c / mt
            rows.append((f"Meetings — {st}", str(c), f"{pct:.1f}% of meeting rows."))

    # Counseling
    cs = totals.get("counseling_total") or 0
    rows.append(("Counseling sessions (all)", str(cs), "Counseling session records."))
    if cs:
        for st in ("scheduled", "completed", "cancelled", "rescheduled", "referred"):
            c = totals.get(f"counseling_{st}") or 0
            pct = 100.0 * c / cs
            rows.append((f"Counseling — {st}", str(c), f"{pct:.1f}% of counseling rows."))

    # Assessments — distinct students with at least one response
    students = totals.get("students") or 0
    for key, label in (
        ("students_psychometric", "Students with psychometric responses"),
        ("students_pf16", "Students with PF16 responses"),
        ("students_ibp", "Students with IBP responses"),
    ):
        n = totals.get(key) or 0
        rows.append((label, str(n), "Distinct students with ≥1 row in the assessment table."))
        if students:
            pct = 100.0 * n / students
            rows.append(
                (
                    f"{label} (% of students)",
                    f"{pct:.1f}%",
                    "Share of registered students who started or completed this assessment.",
                )
            )

    return rows


def main() -> int:
    try:
        import pandas as pd
    except ImportError:
        print("Install: pip install pandas openpyxl")
        return 1

    from app.db.database import SessionLocal

    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    default_name = f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    out_env = os.getenv("OUTPUT_PATH")
    out_path = Path(out_env) if out_env else (project_root / default_name)
    if not out_path.is_absolute():
        out_path = project_root / out_path

    db = SessionLocal()
    try:
        # --- Core totals for insights ---
        totals: dict[str, int | None] = {}
        totals["students"] = _safe_scalar(db, "SELECT COUNT(*) FROM students")
        totals["mentors"] = _safe_scalar(db, "SELECT COUNT(*) FROM mentors")
        totals["students_unassigned"] = _safe_scalar(
            db,
            "SELECT COUNT(*) FROM students WHERE assigned_mentor IS NULL OR assigned_mentor = ''",
        )

        totals["activities_tracking_total"] = _safe_scalar(
            db, "SELECT COUNT(*) FROM activities_tracking"
        )
        for st in ("Approved", "Pending", "Rejected"):
            totals[f"activities_{st.lower()}"] = _safe_scalar(
                db,
                "SELECT COUNT(*) FROM activities_tracking WHERE status = :s",
                {"s": st},
            )

        totals["meetings_total"] = _safe_scalar(db, "SELECT COUNT(*) FROM meetings")
        for st in ("completed", "scheduled", "cancelled"):
            totals[f"meetings_{st}"] = _safe_scalar(
                db,
                "SELECT COUNT(*) FROM meetings WHERE LOWER(TRIM(status)) = :s",
                {"s": st},
            )

        totals["counseling_total"] = _safe_scalar(
            db, "SELECT COUNT(*) FROM counseling_sessions"
        )
        for st in ("scheduled", "completed", "cancelled", "rescheduled", "referred"):
            totals[f"counseling_{st}"] = _safe_scalar(
                db,
                "SELECT COUNT(*) FROM counseling_sessions WHERE LOWER(TRIM(status)) = :s",
                {"s": st},
            )

        totals["students_psychometric"] = _safe_scalar(
            db, "SELECT COUNT(DISTINCT student_usn) FROM psychometric_responses"
        )
        totals["students_pf16"] = _safe_scalar(
            db, "SELECT COUNT(DISTINCT student_usn) FROM pf16_responses"
        )
        totals["students_ibp"] = _safe_scalar(
            db, "SELECT COUNT(DISTINCT student_usn) FROM ibp_responses"
        )

        # --- DataFrames ---
        db_url = os.getenv("DATABASE_URL", "")
        df_meta = pd.DataFrame(
            [
                {"key": "Generated at", "value": generated},
                {"key": "Database (masked)", "value": _mask_db_url(db_url) if db_url else "(default from app.db.database)"},
            ]
        )

        counts = table_counts(db)
        df_counts = pd.DataFrame(counts, columns=["table_name", "row_count"])
        df_counts.insert(0, "rank", range(1, len(df_counts) + 1))

        insight_rows = build_insights(totals)
        df_insights = pd.DataFrame(
            insight_rows, columns=["metric", "value", "analytics_insight"]
        )

        df_students_program = _safe_frame(
            db,
            """
            SELECT COALESCE(NULLIF(TRIM(student_program), ''), '(blank)') AS student_program,
                   COUNT(*) AS cnt
            FROM students
            GROUP BY COALESCE(NULLIF(TRIM(student_program), ''), '(blank)')
            ORDER BY cnt DESC
            """,
            ["student_program", "count"],
        )

        df_students_sem = _safe_frame(
            db,
            """
            SELECT COALESCE(CAST(semester AS CHAR), '(null)') AS semester, COUNT(*) AS cnt
            FROM students
            GROUP BY semester
            ORDER BY semester IS NULL, semester
            """,
            ["semester", "count"],
        )

        df_students_batch = _safe_frame(
            db,
            """
            SELECT COALESCE(NULLIF(TRIM(student_batch), ''), '(blank)') AS student_batch,
                   COUNT(*) AS cnt
            FROM students
            GROUP BY COALESCE(NULLIF(TRIM(student_batch), ''), '(blank)')
            ORDER BY cnt DESC
            """,
            ["student_batch", "count"],
        )

        df_mentors_dept = _safe_frame(
            db,
            """
            SELECT COALESCE(NULLIF(TRIM(mentor_department), ''), '(mentor dept blank)') AS department,
                   COUNT(*) AS cnt
            FROM mentors
            GROUP BY COALESCE(NULLIF(TRIM(mentor_department), ''), '(mentor dept blank)')
            ORDER BY cnt DESC
            """,
            ["department", "count"],
        )

        dept_case = _sql_student_department_expr("s", "m")
        df_students_by_dept = _safe_frame(
            db,
            f"""
            SELECT {dept_case} AS department,
                   COUNT(*) AS student_count
            FROM students s
            LEFT JOIN mentors m ON s.assigned_mentor = m.mentor_id
            GROUP BY 1
            ORDER BY student_count DESC
            """,
            ["department", "student_count"],
        )

        df_activities_by_dept = _safe_frame(
            db,
            f"""
            SELECT {dept_case} AS department,
                   COUNT(*) AS activity_rows
            FROM activities_tracking at
            INNER JOIN students s ON at.student_usn = s.student_usn
            LEFT JOIN mentors m ON s.assigned_mentor = m.mentor_id
            GROUP BY 1
            ORDER BY activity_rows DESC
            """,
            ["department", "activity_rows"],
        )

        df_meetings_by_dept = _safe_frame(
            db,
            f"""
            SELECT {_sql_mentor_department_expr('m')} AS department,
                   COUNT(*) AS meetings_count
            FROM meetings mt
            INNER JOIN mentors m ON mt.mentor_id = m.mentor_id
            GROUP BY 1
            ORDER BY meetings_count DESC
            """,
            ["department", "meetings_count"],
        )

        df_counseling_by_dept = _safe_frame(
            db,
            f"""
            SELECT {_sql_mentor_department_expr('m')} AS department,
                   COUNT(*) AS counseling_count
            FROM counseling_sessions cs
            INNER JOIN mentors m ON cs.mentor_id = m.mentor_id
            GROUP BY 1
            ORDER BY counseling_count DESC
            """,
            ["department", "counseling_count"],
        )

        df_psych_by_dept = _safe_frame(
            db,
            f"""
            SELECT {dept_case} AS department,
                   COUNT(DISTINCT p.student_usn) AS students_psychometric
            FROM psychometric_responses p
            INNER JOIN students s ON p.student_usn = s.student_usn
            LEFT JOIN mentors m ON s.assigned_mentor = m.mentor_id
            GROUP BY 1
            """,
            ["department", "students_psychometric"],
        )

        df_pf16_by_dept = _safe_frame(
            db,
            f"""
            SELECT {dept_case} AS department,
                   COUNT(DISTINCT p.student_usn) AS students_pf16
            FROM pf16_responses p
            INNER JOIN students s ON p.student_usn = s.student_usn
            LEFT JOIN mentors m ON s.assigned_mentor = m.mentor_id
            GROUP BY 1
            """,
            ["department", "students_pf16"],
        )

        df_ibp_by_dept = _safe_frame(
            db,
            f"""
            SELECT {dept_case} AS department,
                   COUNT(DISTINCT p.student_usn) AS students_ibp
            FROM ibp_responses p
            INNER JOIN students s ON p.student_usn = s.student_usn
            LEFT JOIN mentors m ON s.assigned_mentor = m.mentor_id
            GROUP BY 1
            """,
            ["department", "students_ibp"],
        )

        # --- Department summary (mentors + students + workload + funnel metrics) ---
        total_students_int = int(totals["students"] or 0)
        df_mcnt = df_mentors_dept.rename(columns={"count": "mentor_count"})
        df_dept_summary = df_mcnt.merge(df_students_by_dept, on="department", how="outer")
        for extra in (
            df_activities_by_dept,
            df_meetings_by_dept,
            df_counseling_by_dept,
            df_psych_by_dept,
            df_pf16_by_dept,
            df_ibp_by_dept,
        ):
            df_dept_summary = df_dept_summary.merge(extra, on="department", how="outer")
        df_dept_summary = df_dept_summary.fillna(0)
        for col in (
            "mentor_count",
            "student_count",
            "activity_rows",
            "meetings_count",
            "counseling_count",
            "students_psychometric",
            "students_pf16",
            "students_ibp",
        ):
            if col in df_dept_summary.columns:
                df_dept_summary[col] = (
                    pd.to_numeric(df_dept_summary[col], errors="coerce").fillna(0).astype(int)
                )

        def _safe_div(a: float, b: float) -> float | None:
            if b and b != 0:
                return round(float(a) / float(b), 2)
            return None

        df_dept_summary["students_per_mentor"] = df_dept_summary.apply(
            lambda r: _safe_div(r.get("student_count") or 0, r.get("mentor_count") or 0),
            axis=1,
        )
        df_dept_summary["pct_of_all_students"] = df_dept_summary["student_count"].apply(
            lambda sc: round(100.0 * float(sc) / total_students_int, 1) if total_students_int else 0.0
        )
        for assess_col, pct_name in (
            ("students_psychometric", "pct_students_psych_vs_dept"),
            ("students_pf16", "pct_students_pf16_vs_dept"),
            ("students_ibp", "pct_students_ibp_vs_dept"),
        ):
            if assess_col in df_dept_summary.columns:
                df_dept_summary[pct_name] = df_dept_summary.apply(
                    lambda r, c=assess_col: (
                        round(100.0 * float(r.get(c) or 0) / float(r.get("student_count") or 1), 1)
                        if (r.get("student_count") or 0) > 0
                        else 0.0
                    ),
                    axis=1,
                )
        df_dept_summary = df_dept_summary.sort_values("student_count", ascending=False)
        df_dept_summary = _add_department_insights(df_dept_summary, total_students_int)

        col_order = [
            "department",
            "mentor_count",
            "student_count",
            "pct_of_all_students",
            "students_per_mentor",
            "activity_rows",
            "meetings_count",
            "counseling_count",
            "students_psychometric",
            "pct_students_psych_vs_dept",
            "students_pf16",
            "pct_students_pf16_vs_dept",
            "students_ibp",
            "pct_students_ibp_vs_dept",
            "analytics_insight",
        ]
        df_dept_summary = df_dept_summary[
            [c for c in col_order if c in df_dept_summary.columns]
        ]

        df_mentor_load = _safe_frame(
            db,
            """
            SELECT m.mentor_id, m.mentor_name, m.mentor_department AS department,
                   COUNT(s.student_usn) AS assigned_students
            FROM mentors m
            LEFT JOIN students s ON m.mentor_id = s.assigned_mentor
            GROUP BY m.mentor_id, m.mentor_name, m.mentor_department
            ORDER BY assigned_students DESC, m.mentor_name
            """,
            ["mentor_id", "mentor_name", "department", "assigned_students"],
        )

        df_activity_status = _safe_frame(
            db,
            """
            SELECT COALESCE(NULLIF(TRIM(status), ''), '(blank)') AS status, COUNT(*) AS cnt
            FROM activities_tracking
            GROUP BY COALESCE(NULLIF(TRIM(status), ''), '(blank)')
            ORDER BY cnt DESC
            """,
            ["status", "count"],
        )

        df_meetings_month = _safe_frame(
            db,
            """
            SELECT DATE_FORMAT(meeting_date, '%Y-%m') AS month, COUNT(*) AS cnt
            FROM meetings
            GROUP BY DATE_FORMAT(meeting_date, '%Y-%m')
            ORDER BY month DESC
            LIMIT 36
            """,
            ["month", "count"],
        )

        # Psychometric / PF16 / IBP completion (students with at least one row)
        df_psych = _safe_frame(
            db,
            """
            SELECT COUNT(DISTINCT student_usn) AS students_with_psychometric
            FROM psychometric_responses
            """,
            ["students_with_psychometric"],
        )
        df_pf16 = _safe_frame(
            db,
            """
            SELECT COUNT(DISTINCT student_usn) AS students_with_pf16
            FROM pf16_responses
            """,
            ["students_with_pf16"],
        )
        df_ibp = _safe_frame(
            db,
            """
            SELECT COUNT(DISTINCT student_usn) AS students_with_ibp
            FROM ibp_responses
            """,
            ["students_with_ibp"],
        )

        # Single sheet: curated insights first, then full table counts (blank rows between)
        dash_insights = pd.DataFrame(
            [
                {"section": "=== Analytics insights (metric, value, interpretation) ===", "metric": "", "value": "", "analytics_insight": ""},
            ]
        )
        dash_gap = pd.DataFrame([{"section": "", "metric": "", "value": "", "analytics_insight": ""}])
        df_insights_dash = df_insights.copy()
        df_counts_dash = pd.DataFrame(
            {
                "metric": df_counts.apply(
                    lambda r: (
                        f"{r['rank']}. {r['table_name']}"
                        if isinstance(r.get("row_count"), int)
                        else str(r["table_name"])
                    ),
                    axis=1,
                ),
                "value": df_counts["row_count"],
            }
        )
        df_counts_dash["analytics_insight"] = df_counts_dash["value"].apply(
            lambda v: (
                "Table is empty."
                if v == 0
                else ("Table missing or error." if isinstance(v, str) else "Row count for this database table.")
            )
        )

        dash_dept_header = pd.DataFrame(
            [
                {
                    "section": "=== Department insights (students bucketed by assigned mentor dept) ===",
                    "metric": "",
                    "value": "",
                    "analytics_insight": "",
                }
            ]
        )
        df_dept_dash = pd.DataFrame()
        if not df_dept_summary.empty and "error" not in df_dept_summary.columns:
            df_dept_dash = df_dept_summary.head(20).copy()
            df_dept_dash["metric"] = df_dept_dash["department"].astype(str)

            def _fmt_dept_row(r: Any) -> str:
                spm = r.get("students_per_mentor")
                spm_s = f"{float(spm):.2f}" if spm is not None and pd.notna(spm) else "n/a"
                return (
                    f"students={int(r.get('student_count') or 0)}, "
                    f"mentors={int(r.get('mentor_count') or 0)}, spm={spm_s}, "
                    f"activities={int(r.get('activity_rows') or 0)}, "
                    f"meetings={int(r.get('meetings_count') or 0)}, "
                    f"counseling={int(r.get('counseling_count') or 0)}"
                )

            df_dept_dash["value"] = df_dept_dash.apply(_fmt_dept_row, axis=1)

        dash_blocks = [
            dash_insights,
            df_insights_dash.assign(section=""),
        ]
        if not df_dept_dash.empty:
            dash_blocks.extend(
                [
                    dash_gap,
                    dash_dept_header,
                    df_dept_dash[["metric", "value", "analytics_insight"]].assign(section=""),
                ]
            )
        dash_blocks.extend(
            [
                dash_gap,
                pd.DataFrame(
                    [{"section": "=== All table row counts ===", "metric": "", "value": "", "analytics_insight": ""}]
                ),
                df_counts_dash.assign(section=""),
            ]
        )
        df_dashboard = pd.concat(dash_blocks, ignore_index=True)
        df_dashboard = df_dashboard[["section", "metric", "value", "analytics_insight"]]

        with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
            df_meta.to_excel(writer, sheet_name="Report_info", index=False)
            df_dashboard.to_excel(writer, sheet_name="Dashboard_all_counts_insights", index=False)
            df_insights.to_excel(writer, sheet_name="Analytics_insights", index=False)
            df_counts.to_excel(writer, sheet_name="Table_row_counts", index=False)
            df_dept_summary.to_excel(writer, sheet_name="Department_summary", index=False)
            df_students_by_dept.to_excel(writer, sheet_name="Dept_students", index=False)
            df_activities_by_dept.to_excel(writer, sheet_name="Dept_activities", index=False)
            df_meetings_by_dept.to_excel(writer, sheet_name="Dept_meetings", index=False)
            df_counseling_by_dept.to_excel(writer, sheet_name="Dept_counseling", index=False)
            df_psych_by_dept.to_excel(writer, sheet_name="Dept_psychometric", index=False)
            df_pf16_by_dept.to_excel(writer, sheet_name="Dept_pf16", index=False)
            df_ibp_by_dept.to_excel(writer, sheet_name="Dept_ibp", index=False)
            df_students_program.to_excel(writer, sheet_name="Students_by_program", index=False)
            df_students_sem.to_excel(writer, sheet_name="Students_by_semester", index=False)
            df_students_batch.to_excel(writer, sheet_name="Students_by_batch", index=False)
            df_mentors_dept.to_excel(writer, sheet_name="Mentors_by_department", index=False)
            df_mentor_load.to_excel(writer, sheet_name="Mentor_student_load", index=False)
            df_activity_status.to_excel(writer, sheet_name="Activities_by_status", index=False)
            df_meetings_month.to_excel(writer, sheet_name="Meetings_by_month", index=False)
            df_psych.to_excel(writer, sheet_name="Assessments_psych", index=False)
            df_pf16.to_excel(writer, sheet_name="Assessments_pf16", index=False)
            df_ibp.to_excel(writer, sheet_name="Assessments_ibp", index=False)

        print("Written:", out_path.resolve())
        print(
            "Sheets: Report_info, Dashboard_all_counts_insights, Analytics_insights, "
            "Table_row_counts, Department_summary, Dept_*, + other breakdowns."
        )
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
