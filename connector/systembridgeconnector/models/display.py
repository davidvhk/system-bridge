# generated by datamodel-codegen:
#   filename:  display.json

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Extra, Field


class LastUpdated(BaseModel):
    """
    Last updated
    """

    class Config:
        extra = Extra.allow

    displays: Optional[float] = None


class Display(BaseModel):
    """
    Display
    """

    class Config:
        extra = Extra.allow

    id: Optional[str] = Field(None, description="Event ID")
    displays: Optional[list] = None
    last_updated: Optional[LastUpdated] = Field(None, description="Last updated")
