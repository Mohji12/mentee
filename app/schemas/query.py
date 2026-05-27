from pydantic import BaseModel

class QueryWithUSN(BaseModel):
    usn: str
    query_issue: str

# ✅ Schema for new students who **do not have a USN**
class QueryNewStudent(BaseModel):
    usn: str
    name: str
    email: str
    phoneno: str
    program: str
    query_issue: str

# ✅ Response schema (same for both)
class QueryResponse(BaseModel):
    id: str
    usn: str
    name: str
    email: str
    phoneno: str
    program: str
    query_issue: str
    
    class Config:
        from_attributes = True
