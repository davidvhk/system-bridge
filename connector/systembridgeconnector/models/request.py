# generated by datamodel-codegen:
#   filename:  request.json

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Extra, Field


class Request(BaseModel):
    """
    Request
    """

    class Config:
        extra = Extra.allow

    api_key: str = Field(..., alias="api-key", description="API Key")
    id: Optional[str] = Field(None, description="Message ID")
    event: str = Field(..., description="Event")
