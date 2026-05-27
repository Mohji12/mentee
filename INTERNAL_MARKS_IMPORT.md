# Consolidated internal marks (mentor import + mentor view)

## Database

Run once (or rely on SQLAlchemy `create_all` after deploy):

- SQL script: [create_internal_marks_tables.sql](create_internal_marks_tables.sql)

## Mentor import (JWT mentor role)

**Endpoint:** `POST /mentor/{mentor_id}/internal-marks/import`  
**Auth:** Bearer token (JWT with `role` = `mentor` and `ms_ids` = `mentor_id`).

**Content-Type:** `multipart/form-data`

| Field | Required | Notes |
|-------|----------|--------|
| `semester` | Yes | Integer 1–8 |
| `file` | Yes | `.csv` or `.xlsx` |
| `section_code` | No | e.g. `5PMCSA` |
| `program_label` | No | Shown on grid header |
| `branch_label` | No | Shown on grid header |
| `title` | No | Free-text report title |
| `academic_year` | No | e.g. `2024-25` |

**Restriction:** Only rows whose `student_usn` is **assigned to you** (`assigned_mentor` = `mentor_id`) are imported. Other rows are skipped and listed in `errors`.

### File columns (header row)

Required (names are case-insensitive; spaces/underscores accepted):

- **student_usn** — or `usn`, `student_code`
- **subject_code** — or `course_code`
- **component_label** — or `component`, `assessment`
- **score** — or `marks`, `value`

Optional:

- **subject_name** — or `course_name`

Each row is one cell (one student, one subject, one component).

### Example `curl`

```bash
curl -X POST "https://YOUR_API/mentor/YOUR_MENTOR_ID/internal-marks/import" \
  -H "Authorization: Bearer YOUR_MENTOR_JWT" \
  -F "semester=5" \
  -F "section_code=5PMCSA" \
  -F "title=Consolidated Final Internal Marks" \
  -F "file=@internal_marks.csv"
```

## Mentor UI

- Path: `/mentor/{mentor_id}/consolidated-internal-marks`
- Sidebar: **Internal Marks**
- **Upload CSV/Excel** on the same page (import for your mentees only).
- **Download template** — sample header row for your sheet.
- **Import batch:** “Latest (auto)” or pick a specific batch.
- **Download CSV** exports the current grid (UTF-8 BOM for Excel).

## Mentor APIs

- `POST /mentor/{mentor_id}/internal-marks/import`
- `GET /mentor/{mentor_id}/internal-marks/batches?semester={n}`
- `GET /mentor/{mentor_id}/internal-marks/matrix?semester={n}&batch_id={optional}`
