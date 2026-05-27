from pydantic import BaseModel, Field
from typing import List, Optional


class InternalMarksBatchMeta(BaseModel):
    id: int
    semester: int
    section_code: Optional[str] = None
    program_label: Optional[str] = None
    branch_label: Optional[str] = None
    title: Optional[str] = None
    academic_year: Optional[str] = None


class InternalMarksBatchListItem(BaseModel):
    id: int
    semester: int
    section_code: Optional[str] = None
    title: Optional[str] = None
    created_at: Optional[str] = None
    row_count: int = 0


class MatrixComponent(BaseModel):
    component_key: str
    component_label: str
    sort_order: int = 0


class MatrixSubject(BaseModel):
    subject_code: str
    subject_name: Optional[str] = None
    components: List[MatrixComponent] = Field(default_factory=list)


class FlatColumn(BaseModel):
    subject_code: str
    subject_name: Optional[str] = None
    component_key: str
    component_label: str
    sort_order: int = 0


class MatrixStudentRow(BaseModel):
    student_usn: str
    student_name: Optional[str] = None
    scores: List[Optional[str]] = Field(
        default_factory=list,
        description="Parallel to flat_columns; null if no score",
    )


class InternalMarksMatrixResponse(BaseModel):
    batch: Optional[InternalMarksBatchMeta] = None
    subjects: List[MatrixSubject] = Field(default_factory=list)
    flat_columns: List[FlatColumn] = Field(default_factory=list)
    students: List[MatrixStudentRow] = Field(default_factory=list)


class InternalMarksImportResult(BaseModel):
    batch_id: int
    rows_inserted: int
    rows_updated: int
    rows_skipped: int
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
