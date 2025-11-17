"""Selector data model."""

from typing import Literal

from pydantic import BaseModel, field_validator


class Selector(BaseModel):
    """A CSS or XPath selector."""

    selector_type: Literal["css", "xpath"]
    value: str
    description: str

    @field_validator("value")
    @classmethod
    def validate_selector(cls, v: str, info: any) -> str:
        """Basic validation of selector syntax."""
        selector_type = info.data.get("selector_type")

        if selector_type == "css" and "//" in v:
            raise ValueError("CSS selector should not contain XPath syntax (//)")

        if selector_type == "xpath" and not v.startswith(("/", "(")):
            raise ValueError("XPath should start with / or (")

        return v
