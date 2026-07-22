# Concept by MrHan (08974747477)
"""Schemas for master data: categories, responsible parties, meetings,
meeting occurrences, and app settings."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ---- Categories / Responsible Parties / Meetings share a simple shape ----
class NamedCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None


class NamedUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None


class NamedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ---- Meeting occurrences ----
class MeetingOccurrenceCreate(BaseModel):
    meeting_id: uuid.UUID
    meeting_date: date
    meeting_number: str | None = Field(default=None, max_length=50)
    reference_number: str | None = Field(default=None, max_length=100)
    agenda: str | None = None
    minutes_link: str | None = None
    notes: str | None = None


class MeetingOccurrenceUpdate(BaseModel):
    meeting_date: date | None = None
    meeting_number: str | None = Field(default=None, max_length=50)
    reference_number: str | None = Field(default=None, max_length=100)
    agenda: str | None = None
    minutes_link: str | None = None
    notes: str | None = None


class MeetingOccurrenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    meeting_id: uuid.UUID
    meeting_date: date
    meeting_number: str | None
    reference_number: str | None
    agenda: str | None
    minutes_link: str | None
    notes: str | None
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ---- App settings ----
class AppSettingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    value: Any
    description: str | None
    updated_at: datetime


class AppSettingUpdate(BaseModel):
    value: Any
