# generated by datamodel-codegen:
#   filename:  battery.json

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class LastUpdated(BaseModel):
    """
    Last updated
    """

    is_charging: Optional[float] = None
    percentage: Optional[float] = None


class Battery(BaseModel):
    """
    Battery
    """

    id: Optional[str] = Field(None, description="Event ID")
    is_charging: Optional[bool] = None
    percentage: Optional[float] = None
    last_updated: Optional[LastUpdated] = Field(None, description="Last updated")
