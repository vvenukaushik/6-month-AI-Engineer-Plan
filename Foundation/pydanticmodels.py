from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import Field, BaseModel, field_validator, model_validator, ConfigDict


# ══════════════════════════════════════════════════════════════
# MODEL 1: UserProfile
# ══════════════════════════════════════════════════════════════
# Teaches: basic fields, Field() with constraints, Optional, defaults

class UserProfile(BaseModel):
    name: str = Field(
        max_length=100,
        min_length=1,
        description="User display name"
    )
    email: str = Field(
        pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$',
        description="valid email address"
    )
    age: int = Field(
        default=None,
        ge=0,
        le=50,
        description="User's age"
    )
    bio: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Short biography"
    )

    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    # default_factory calls the function at creation time (not import time)
    # This ensures each user gets their OWN timestamp, not a shared one

    #Always use default_factory for the mutable objs like lists,dicts, etc
    tags: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty_spaces(cls, v:str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be the white space")
        return v.strip()
    
    @field_validator("email")
    @classmethod
    def email_must_be_lowercase(clas, v: str) -> str:
        #Normalize email to lower case
        return v.lower()
    

# ══════════════════════════════════════════════════════════════
# MODEL 2: APIResponse (Generic response wrapper)
# ══════════════════════════════════════════════════════════════
# Teaches: Literal, nested models, model_dump(), computed fields

from typing import Any, Literal

class APIResponse(BaseModel):
    """
    Standard API response format. You'll use this pattern in every
    FastAPI app you build.
    
    Teaches:
    - Literal for restricting values
    - Optional nested data
    - model_dump() for converting to dict/JSON
    """

    status: Literal["success", "error"]
    status_code: int = Field(ge=100, le=599)
    message: str
    data: Optional[dict[str,Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    @property
    def is_success(self) -> bool:
         #Computed property — not stored, calculated on access.
        return self.status == "success"
    

# ══════════════════════════════════════════════════════════════
# MODEL 3: ChatMessage (LLM conversation format)
# ══════════════════════════════════════════════════════════════
# Teaches: Enum, nested models, list of models, model_validator

class Role(str, Enum):
    # Enum that is also a string — can be used in JSON directly.
    
    # str, Enum inheritance means:
    #   Role.SYSTEM == "system"  → True
    #   Role.SYSTEM.value        → "system"
    
    # This is cleaner than Literal for values used in multiple places.
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

class ChatMessage(BaseModel):
    """
    Mirrors the exact format that OpenAI and Anthropic APIs use.
    In Month 2, you'll send lists of these to LLM APIs.
    """
    role: Role
    content: str = Field(min_length=1)

    name: Optional[str] = None
    tool_call_id: Optional[str] = None


    model_config = ConfigDict(
        # This allows creating ChatMessage from dicts with extra fields
        # without raising errors (useful when parsing API responses)
        extra="ignore",
        use_enum_values=True,
    )

