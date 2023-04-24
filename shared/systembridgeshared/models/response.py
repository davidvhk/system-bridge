# generated by datamodel-codegen:
#   filename:  response.json

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class Response(BaseModel):
    """
    Response
    """

    id: Optional[str] = Field(None, description="Message ID")
    type: str = Field(..., description="Type")
    subtype: Optional[str] = Field(None, description="Subtype")
    message: Optional[str] = Field(None, description="Message")
    module: Optional[str] = Field(None, description="Module")
    data: Optional[Any] = Field(None, description="Data")
