from typing import List, Optional, Dict, Any
from sqlmodel import Field, SQLModel, Column, JSON
from datetime import datetime
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.types import TypeDecorator

class ListType(TypeDecorator):
    """Custom type for storing lists in SQLite/PostgreSQL."""
    impl = JSON

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        return value

    def process_result_value(self, value: Any, dialect: Any) -> List[Any]:
        return value or []

class Problem(SQLModel, table=True):
    # Core Problem Information (your existing list + slug)
    id: Optional[int] = Field(default=None, primary_key=True) # e.g., LeetCode problem number (can be auto-generated or explicitly set)
    title: str = Field(index=True, unique=True, max_length=255) # The problem title
    slug: str = Field(index=True, unique=True, max_length=255) # Crucial for clean URLs (e.g., /problems/two-sum)
    difficulty: str = Field(max_length=50) # 'Easy', 'Medium', 'Hard'
    tags: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False, server_default='[]')
    )  # A list of different tags (e.g., 'Arrays', 'Hash Maps')

    # Problem Description Content
    problem_markdown: str = Field(sa_column=TEXT) # The full problem description in Markdown format

    # Solution Content (for the primary solution provided by your app)
    solution_code: str = Field(sa_column=TEXT) # The raw code of the solution (for the debugger)
    solution_explanation_markdown: str = Field(sa_column=TEXT) # The explanation of the solution in Markdown

    # Debugger Data
    trace_data: Optional[Dict] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True)
    )  # The pre-generated debugger trace (JSON) for this solution code

    # Optional: Timestamps for record management
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # You might also add:
    # examples: List[Dict[str, str]] = Field(default_factory=list, sa_column=JSONB) # Input/output examples
    # constraints: List[str] = Field(default_factory=list, sa_column=JSONB) # Problem constraints