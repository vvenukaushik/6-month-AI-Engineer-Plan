from auth import hash_password;
from sqlalchemy.orm import Session
from models import User, Notes
from schemas import NoteCreate, NoteUpdate
from sqlalchemy import or_

def create_user(db: Session, username: str, password: str) -> User:
    user = User(username=username, hashed_password = hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(User)
    return user

def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def create_note(db: Session, note_data: NoteCreate, owner_id:int | None) -> Notes:
    note = Notes(
        title=note_data.title,
        content = note_data.content,
        tags_str=",".join(note_data.tags),
        owner_id=owner_id
    )

    db.add(note); db.commit(); db.refresh(note)
    return note

def get_notes(db, skip=0, limit=20, tag=None, keyword=None) -> list[Notes]:
    query = db.query(Notes)
    if tag:
        query = query.filter(Notes.tags_str.ilike(f"%{tag}%"))
    if keyword:
        query = query.filter(or_(
            Notes.title.ilike(f"%{keyword}%"),
            Notes.content.ilike(f"%{keyword}%")
        ))

    return (
        query
        .order_by(Notes.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_note(db, note_id: int) -> Notes | None:
    query = db.query(Notes).filter(Notes.id == note_id)
    return query.first()

def update_note(db:Session, note: Notes, updates: NoteUpdate) -> Notes:
    update_data = updates.model_dump(exclude_unset=True)

    if "tags" in update_data:
        tags_list = update_data.pop("tags")
        note.tags_str = ','.join(tags_list)

    for key, value in update_data.items():
        setattr(note, key, value)

    db.commit()
    db.refresh(note)

    return note

def delete_note(db:Session, note: Notes) -> None:

    db.delete(note)
    db.commit()

def get_note_count(db: Session) -> int:
    return db.query(Notes).count()


