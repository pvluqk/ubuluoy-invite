import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
DB_PATH = Path(os.getenv("DB_PATH", str(BASE_DIR / "rsvp.db")))
ADMIN_KEY = os.getenv("ADMIN_KEY", "ubuluoy-secret-2026")

EVENT_DATE_LABEL = "Алтынньы 4 күнэ · 14:00"
EVENT_PLACE = "Аадырыһа сотору биллэриллиэ"
EVENT_PLACE_NAME = "Сир аата"
EVENT_MAP_URL = os.getenv(
    "EVENT_MAP_URL",
    "https://yandex.ru/maps/?text=%D0%AF%D0%BA%D1%83%D1%82%D1%81%D0%BA",
)
EVENT_ISO = os.getenv("EVENT_ISO", "2026-10-04T14:00:00+09:00")
CONTACT_NAME = "Ыйытыыларга"
CONTACT_PHONE = "+7 (___) ___-__-__"

app = FastAPI(title="Үбүлүөй ыҥырыыта")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rsvps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                coming INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


@app.on_event("startup")
def on_startup() -> None:
    init_db()


def page_context(request: Request, **extra):
    ctx = {
        "request": request,
        "event_date": EVENT_DATE_LABEL,
        "event_place": EVENT_PLACE,
        "event_place_name": EVENT_PLACE_NAME,
        "event_map_url": EVENT_MAP_URL,
        "event_iso": EVENT_ISO,
        "contact_name": CONTACT_NAME,
        "contact_phone": CONTACT_PHONE,
    }
    ctx.update(extra)
    return ctx


class RsvpIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    coming: bool


@app.get("/", response_class=HTMLResponse)
def invite_page(request: Request):
    return templates.TemplateResponse("index.html", page_context(request))


@app.post("/api/rsvp")
async def create_rsvp(payload: RsvpIn):
    name = " ".join(payload.name.split())
    if not name:
        raise HTTPException(status_code=400, detail="Аатыҥ суох")
    created_at = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        conn.execute(
            "INSERT INTO rsvps (name, coming, created_at) VALUES (?, ?, ?)",
            (name, 1 if payload.coming else 0, created_at),
        )
    return {"ok": True, "name": name, "coming": payload.coming}


@app.post("/rsvp", response_class=HTMLResponse)
async def create_rsvp_form(
    request: Request,
    coming: str = Form(...),
    firstname: str = Form(...),
    surname: str = Form(""),
):
    cleaned = " ".join(f"{surname} {firstname}".split())
    if not cleaned:
        raise HTTPException(status_code=400, detail="Аатыҥ суох")
    is_coming = coming.lower() in {"yes", "1", "true", "да", "хайаан"}
    created_at = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        conn.execute(
            "INSERT INTO rsvps (name, coming, created_at) VALUES (?, ?, ?)",
            (cleaned, 1 if is_coming else 0, created_at),
        )
    return templates.TemplateResponse(
        "index.html",
        page_context(
            request,
            submitted=True,
            guest_name=cleaned,
            guest_coming=is_coming,
        ),
    )


def require_admin(key: str | None) -> None:
    if not key or key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Киирии бобуллубут")


@app.get("/api/guests")
def list_guests_api(key: str = Query(default="")):
    require_admin(key)
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, name, coming, created_at FROM rsvps ORDER BY created_at DESC"
        ).fetchall()
    guests = [
        {
            "id": row["id"],
            "name": row["name"],
            "coming": bool(row["coming"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
    coming_count = sum(1 for g in guests if g["coming"])
    return {
        "total": len(guests),
        "coming": coming_count,
        "not_coming": len(guests) - coming_count,
        "guests": guests,
    }


@app.get("/guests", response_class=HTMLResponse)
def guests_page(request: Request, key: str = Query(default="")):
    require_admin(key)
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, name, coming, created_at FROM rsvps ORDER BY created_at DESC"
        ).fetchall()
    guests = [dict(row) for row in rows]
    coming_count = sum(1 for g in guests if g["coming"])
    return templates.TemplateResponse(
        "guests.html",
        {
            "request": request,
            "key": key,
            "guests": guests,
            "total": len(guests),
            "coming": coming_count,
            "not_coming": len(guests) - coming_count,
        },
    )


@app.get("/admin")
def admin_redirect(key: str = Query(default="")):
    if key:
        return RedirectResponse(url=f"/guests?key={key}")
    raise HTTPException(status_code=403, detail="Киирии бобуллубут")
