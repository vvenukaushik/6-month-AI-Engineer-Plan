from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from config import APP_TITLE, APP_VERSION
from middleware import logging_middleware
from fastapi import Depends, HTTPException, Query, Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user, verify_password, create_access_token
import crud as crud
import asyncio
from fastapi.responses import StreamingResponse
import schemas as schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION
)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

app.middleware("http")(logging_middleware)


@app.post("/auth/register", response_model=schemas.UserResponse, status_code=201)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user_data.username):
        raise HTTPException(400, "Username taken.")
    return crud.create_user(db, user_data.username, user_data.password)

@app.post("/auth/login", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Bad credentials.")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/notes", response_model=schemas.NoteListResponse)
def list_notes(
    tag: str | None = None,
    keyword: str | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    notes = crud.get_notes(db, skip=skip, limit=limit, tag=tag, keyword=keyword)
    return {"count": len(notes), "notes": notes}

@app.post("/notes", response_model=schemas.NoteResponse, status_code=201)
def create_note(
    data: schemas.NoteCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),     # ← THE GUARD!
):
    return crud.create_note(db, data, owner_id=user.id)

@app.get("/notes/{note_id}", response_model=schemas.NoteResponse, tags=["Notes"])
def get_note(
    note_id: int = Path(..., ge=1),      # Path param: must be >= 1
    db: Session = Depends(get_db),
):
    """Get a single note by ID. PUBLIC — no auth needed."""
    note = crud.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail=f"Note {note_id} not found.")
    return note


@app.patch("/notes/{note_id}", response_model=schemas.NoteResponse, tags=["Notes"])
def update_note(
    note_id: int,
    updates: schemas.NoteUpdate,              # Request body — only changed fields
    db: Session = Depends(get_db),
    user = Depends(get_current_user),         # ← PROTECTED!
):
    """Update a note partially. PROTECTED — requires auth."""
    note = crud.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail=f"Note {note_id} not found.")
    return crud.update_note(db, note, updates)


@app.delete("/notes/{note_id}", tags=["Notes"])
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),         # ← PROTECTED!
):
    """Delete a note. PROTECTED — requires auth."""
    note = crud.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail=f"Note {note_id} not found.")
    crud.delete_note(db, note)
    return {"message": f"Note {note_id} deleted."}


async def fake_sumary(note):
    fake_sum = f"Summary of '{note.title}': This note about " \
           f"{', '.join(note.tags) or 'general topics'} covers..."
    
    for char in fake_sum:
        yield char
        await asyncio.sleep(0.05)


@app.get("/notes/{note_id}/summary")
async def fake_summary(note_id: int, db: Session = Depends(get_db)):
    note = crud.get_note(db, note_id)
    if not note:
        raise HTTPException(404, "Note not found")
    return StreamingResponse(fake_summary(note), media_type="text/plain")