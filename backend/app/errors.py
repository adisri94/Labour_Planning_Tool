"""Shared validation error type / envelope.

Interim shape per docs/features/01-facility-org-master-data.md Section 8 --
{"error": "...", "field": "..."} -- to be reconciled with whatever Feature 10
(Sprint 8) standardizes for the whole API.
"""
from fastapi import HTTPException


class ValidationError(HTTPException):
    def __init__(self, message: str, field: str | None = None):
        super().__init__(status_code=422, detail={"error": message, "field": field})
