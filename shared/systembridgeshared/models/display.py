# generated by datamodel-codegen:
#   filename:  display.json

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class LastUpdated(BaseModel):
    """
    Last updated
    """

    displays: Optional[float] = None


class Display(BaseModel):
    """
    Display
    """

    id: Optional[str] = Field(None, description="Event ID")
    displays: Optional[list] = None
    last_updated: Optional[LastUpdated] = Field(None, description="Last updated")
