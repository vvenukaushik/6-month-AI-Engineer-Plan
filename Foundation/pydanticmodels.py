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

class Conversation(BaseModel):
    """A full conversation (list of messages).
    Teaches: list of nested models, model_validator for cross-field validation.
    """
    messages: list[ChatMessage] = Field(default_factory=list)
    model: str = Field(default="gpt-4o-mini")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=128000)

    @model_validator(mode="after")
    def validate(self) -> Conversation:
        if self.messages and self.messages[0].role != Role.SYSTEM:
            pass
        return self

    def add_message(self, role: Role, content: str) -> None:
        self.messages.append(ChatMessage(role=role, content=content))

    @property
    def total_chars(self) -> int:
        return sum(len(m.content) for m in self.messages)
    
    @property
    def estimated_tokens(self) -> int:
        return self.total_chars // 4
    
# ══════════════════════════════════════════════════════════════
# MODEL 4: ToolCall (Function calling format)
# ══════════════════════════════════════════════════════════════
# Teaches: nested models, JSON serialization, discriminated unions

class ToolParameter(BaseModel):
    name: str
    value: str | int | float | bool | list[str]


class ToolCall(BaseModel):
    """
    Represents an LLM requesting to call a function/tool.
    In Month 2, you'll implement tool calling where the LLM
    returns these structured objects, and your code executes
    the actual function.
    
    Real OpenAI tool call format:
    {
        "id": "call_abc123",
        "type": "function",
        "function": {
            "name": "get_weather",
            "arguments": '{"city": "London", "units": "celsius"}'
        }
    }
    """
    id: str = Field(description="Unique Identifier for this tool call")
    tool_name : str = Field(
        min_length=1,
        pattern=r'^[a-z_][a-z0-9_]*$',
        description="Function Name (snake_case only)"
    )
    parameters: dict[str, str | int | float | bool | list[str]] = Field(default_factory=dict, description="Arguments to pass function")

    #Tracking fields
    status: Literal["pending", "running", "completed", "failed"] = "pending"
    result: Optional[str] = None
    error: Optional[str] = None
    executed_at: Optional[datetime] = None

    def mark_completed(self, result: str) -> None:
        """Mark this tool call as successfully completed."""
        self.status = "completed"
        self.result = result
        self.executed_at = datetime.now()

    def mark_failed(self, error:str) -> None:
        self.status = "failed"
        self.error = error
        self.executed_at = datetime.now()

    
# ══════════════════════════════════════════════════════════════
# MODEL 5: ErrorResponse (Structured error handling)
# ══════════════════════════════════════════════════════════════
# Teaches: class methods as factory constructors, JSON schema export

class ErrorSeverity(str, Enum):
    LOW="low"
    MEDIUM="medium"
    HIGH="HIGH"
    CRITICAL="critical"

class ErrorResponse(BaseModel):
    """
    Structured error response for AI applications.
    Instead of returning raw error strings, production apps
    return structured errors that frontends can parse and display.
    
    Teaches: @classmethod factories — a clean pattern for creating
    instances with pre-filled fields.
    """
    error_code : str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readble error message")
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    details: Optional[dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    retry_after: Optional[int] = Field(
        default=None,
        ge=0,
        description="Seconds to wait before retrying"
    )

    @classmethod
    def rate_limited(cls, retry_after: int = 60) -> ErrorResponse:
        return cls(
            error_code="RATE_LIMITED",
            message = "Too many requests",
            severity=ErrorSeverity.MEDIUM,
            retry_after=retry_after
        )
    
    @classmethod
    def model_error(cls, model_name: str, detail: str) -> ErrorResponse:
        return cls(
            error_code="MODEL_ERROR",
            message=f"Model '{model_name}' returned an error",
            severity=ErrorSeverity.HIGH,
            details={"model": model_name, "detail": detail},
        )

    @classmethod
    def validation_error(cls, field: str, issue: str) -> ErrorResponse:
        return cls(
            error_code="VALIDATION_ERROR",
            message=f"Invalid input for field '{field}': {issue}",
            severity=ErrorSeverity.LOW,
            details={"field": field, "issue": issue},
        )


# ══════════════════════════════════════════════════════════════
# DEMO: Using all five models
# ══════════════════════════════════════════════════════════════
 
if __name__ == "__main__":
    import json
    
    print("=" * 60)
    print("PYDANTIC MODELS — FIVE AI ENGINEERING PATTERNS")
    print("=" * 60)
    
    # ── MODEL 1: UserProfile ──────────────────────────────
    print("\n" + "─" * 60)
    print("MODEL 1: UserProfile")
    print("─" * 60)
    
    user = UserProfile(
        name="  Alice Chen  ",   # Will be stripped by validator
        email="Alice@Example.COM",  # Will be lowercased
        age=28,
        bio="AI engineer building cool stuff",
        tags=["python", "ai", "rag"],
    )
    print(f"   Created: {user.name} ({user.email})")
    print(f"   Active: {user.is_active}, Tags: {user.tags}")
    
    # model_dump() converts to a dict (for JSON serialization)
    user_dict = user.model_dump()
    print(f"   model_dump() keys: {list(user_dict.keys())}")
    
    # Validation errors
    print("\n   Testing validation errors:")
    from pydantic import ValidationError
    
    bad_inputs = [
        {"desc": "empty name", "data": {"name": "", "email": "a@b.com", "age": 25}},
        {"desc": "bad email", "data": {"name": "Bob", "email": "not-an-email", "age": 25}},
        {"desc": "negative age", "data": {"name": "Bob", "email": "b@b.com", "age": -5}},
        {"desc": "whitespace name", "data": {"name": "   ", "email": "b@b.com", "age": 25}},
    ]
    for case in bad_inputs:
        try:
            UserProfile(**case["data"])
            print(f"   ❌ {case['desc']}: should have failed!")
        except ValidationError as e:
            error_count = e.error_count()
            print(f"   ✅ {case['desc']}: caught {error_count} error(s)")
    
    # ── MODEL 2: APIResponse ─────────────────────────────
    print("\n" + "─" * 60)
    print("MODEL 2: APIResponse")
    print("─" * 60)
    
    success = APIResponse(
        status="success",
        status_code=200,
        message="Data retrieved successfully",
        data={"users": [{"id": 1, "name": "Alice"}]},
    )
    print(f"   Status: {success.status} (is_success={success.is_success})")
    
    error = APIResponse(
        status="error",
        status_code=404,
        message="User not found",
    )
    print(f"   Error: {error.message} (is_success={error.is_success})")
    
    # model_dump_json() gives you a JSON string directly
    print(f"   JSON: {success.model_dump_json(indent=2)[:80]}...")
    
    # ── MODEL 3: ChatMessage & Conversation ──────────────
    print("\n" + "─" * 60)
    print("MODEL 3: ChatMessage & Conversation")
    print("─" * 60)
    
    conv = Conversation(model="gpt-4o", temperature=0.3)
    conv.add_message(Role.SYSTEM, "You are a helpful AI assistant.")
    conv.add_message(Role.USER, "What is machine learning?")
    conv.add_message(Role.ASSISTANT, "Machine learning is a subset of AI...")
    
    print(f"   Model: {conv.model}, Temp: {conv.temperature}")
    print(f"   Messages: {len(conv.messages)}")
    for msg in conv.messages:
        preview = msg.content[:40] + "..." if len(msg.content) > 40 else msg.content
        print(f"     [{msg.role}] {preview}")
    print(f"   Estimated tokens: ~{conv.estimated_tokens}")
    
    # This is the exact format you'd send to an API
    api_payload = conv.model_dump()
    print(f"   API payload keys: {list(api_payload.keys())}")
    
    # ── MODEL 4: ToolCall ────────────────────────────────
    print("\n" + "─" * 60)
    print("MODEL 4: ToolCall")
    print("─" * 60)
    
    tool = ToolCall(
        id="call_abc123",
        tool_name="get_weather",
        parameters={"city": "London", "units": "celsius"},
    )
    print(f"   Tool: {tool.tool_name}({tool.parameters})")
    print(f"   Status: {tool.status}")
    
    # Simulate execution
    tool.mark_completed("Temperature: 18°C, Partly cloudy")
    print(f"   After execution: status={tool.status}")
    print(f"   Result: {tool.result}")
    
    # Failed tool call
    failed_tool = ToolCall(
        id="call_def456",
        tool_name="search_database",
        parameters={"query": "quarterly revenue"},
    )
    failed_tool.mark_failed("Database connection timeout")
    print(f"   Failed tool: status={failed_tool.status}, error={failed_tool.error}")
    
    # ── MODEL 5: ErrorResponse ───────────────────────────
    print("\n" + "─" * 60)
    print("MODEL 5: ErrorResponse (Factory methods)")
    print("─" * 60)
    
    # Using factory methods (cleaner than manually filling all fields)
    rate_err = ErrorResponse.rate_limited(retry_after=30)
    print(f"   Rate limited: {rate_err.error_code} — retry in {rate_err.retry_after}s")
    
    model_err = ErrorResponse.model_error("gpt-4o", "Context window exceeded")
    print(f"   Model error: {model_err.message}")
    print(f"   Details: {model_err.details}")
    
    val_err = ErrorResponse.validation_error("email", "Invalid format")
    print(f"   Validation: {val_err.message}")
    
    # ── BONUS: JSON Schema export ────────────────────────
    print("\n" + "─" * 60)
    print("BONUS: JSON Schema Export")
    print("─" * 60)
    
    schema = ChatMessage.model_json_schema()
    print(f"   ChatMessage schema:")
    print(f"   {json.dumps(schema, indent=2)[:200]}...")
    print()
    print("   WHY THIS MATTERS: In Month 2, you'll pass these schemas to")
    print("   LLM APIs for structured outputs. The model reads the schema")
    print("   and returns data that matches it exactly.")
    
    print()
    print("🎓 KEY TAKEAWAYS:")
    print("   1. BaseModel validates data at creation time — bad data never enters your system")
    print("   2. Field() adds constraints: min/max length, regex patterns, numeric ranges")
    print("   3. @field_validator = custom single-field logic (strip, normalize, check)")
    print("   4. @model_validator = cross-field logic (field A depends on field B)")
    print("   5. model_dump() → dict, model_dump_json() → JSON string")
    print("   6. model_json_schema() → JSON Schema (used by LLM structured outputs)")
    print("   7. @classmethod factories = clean way to create pre-configured instances")