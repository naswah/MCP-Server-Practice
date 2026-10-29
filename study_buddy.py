import sqlite3
from contextlib import closing
from datetime import date, datetime
from pathlib import Path

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

mcp= MCPServer("study_buddy")

DB= Path(__file__).parent / "study_buddy.db"

# database helpers

def query_db(sql: str, params: tuple=())-> list:
    "Run a SELECT and return all rows"
    with closing(sqlite3.connect(DB)) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(sql, params).fetchall()


def execute_query(sql: str, params: tuple=())-> list:
    with closing(sqlite3.connect(DB)) as conn:
        cur= conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid


def setup() -> None:
    execute_query(
        "CREATE TABLE IF NOT EXISTS notes ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "subject TEXT, title TEXT, body TEXT, created TEXT)"
    )
    execute_query(
        "CREATE TABLE IF NOT EXISTS sessions ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "subject TEXT, minutes INTEGER, day TEXT)"
    )

setup()

#MCP TOOLS

@mcp.tool()
def add_note(subject: str, title: str, body: str) -> str:
    """Save a study note under a subject (for example: biology, math)."""
    if not title.strip() or not body.strip():
        raise ToolError("Title and body cannot be empty.")
    note_id = execute_query(
        "INSERT INTO notes (subject, title, body, created) VALUES (?, ?, ?, ?)",
        (subject.lower().strip(), title.strip(), body.strip(), str(date.today())),
    )
    return f"Saved note #{note_id} under '{subject.lower().strip()}'."


@mcp.tool()
def search_notes(keyword: str) -> str:
    """Find notes whose subject, title, or text contains a keyword."""
    like = f"%{keyword.strip()}%"
    rows = query_db(
        "SELECT id, subject, title FROM notes WHERE subject LIKE ? OR title LIKE ? OR body LIKE ?",
        (like, like, like),
    )
    if not rows:
        return f"No notes found for '{keyword}'."
    return "\n".join(f"#{r['id']} [{r['subject']}] {r['title']}" for r in rows)


@mcp.tool()
def list_notes() -> str:
    """List all saved notes with their ID, subject, title, and date."""
    rows = query_db("SELECT id, subject, title, created FROM notes ORDER BY id")
    if not rows:
        return "No notes saved yet."
    return "\n".join(
        f"#{r['id']} [{r['subject']}] {r['title']} ({r['created']})" for r in rows
    )


@mcp.tool()
def log_study_time(subject: str, minutes: int) -> str:
    """Record how many minutes the user studied a subject today."""
    if minutes <= 0 or minutes > 1000:
        raise ToolError("Minutes must be between 1 and 1000.")
    execute_query(
        "INSERT INTO sessions (subject, minutes, day) VALUES (?, ?, ?)",
        (subject.lower().strip(), minutes, str(date.today())),
    )
    return f"Logged {minutes} minutes of {subject.lower().strip()}."


@mcp.tool()
def study_stats() -> dict:
    """Total study minutes for each subject, across all days."""
    rows = query_db("SELECT subject, SUM(minutes) AS total FROM sessions GROUP BY subject")
    return {r["subject"]: r["total"] for r in rows}


@mcp.resource("study://today")
def today_summary() -> str:
    """Minutes studied today, per subject."""
    rows = query_db(
        "SELECT subject, SUM(minutes) AS total FROM sessions WHERE day = ? GROUP BY subject",
        (str(date.today()),),
    )
    if not rows:
        return "Nothing logged today yet."
    return "\n".join(f"{r['subject']}: {r['total']} min" for r in rows)


@mcp.resource("notes://subject/{subject}")
def notes_by_subject(subject: str) -> str:
    """All notes saved under one subject."""
    rows = query_db(
        "SELECT title, body FROM notes WHERE subject = ?", (subject.lower().strip(),)
    )
    if not rows:
        return f"No notes for '{subject}'."
    return "\n\n".join(f"## {r['title']}\n{r['body']}" for r in rows)


@mcp.resource("notes://all")
def all_notes() -> str:
    """Every saved note, with its full text."""
    rows = query_db("SELECT subject, title, body FROM notes ORDER BY subject, id")
    if not rows:
        return "No notes saved yet."
    return "\n\n".join(f"[{r['subject']}] {r['title']}\n{r['body']}" for r in rows)


@mcp.prompt()
def quiz_me(subject: str, number_of_questions: str) -> str:
    return (
        f"Read my notes for '{subject}' using the notes://subject/{subject} resource "
        f"or the search_notes tool. Then quiz me with {number_of_questions} questions, "
        "one at a time. Wait for my answer, tell me if I'm right, and give a final score."
    )


if __name__ == "__main__":
    mcp.run()