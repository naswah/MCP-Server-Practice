import json
from pathlib import Path
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("todo-helper")

FILE= Path(__file__).parent / "tasks.json"

def load_tasks() -> list:
    """Load tasks from the JSON file."""
    if FILE.exists():
        return json.loads(FILE.read_text(encoding="utf-8"))
    return []

def save_tasks(tasks: list) -> None:
    """Write tasks to the file."""
    FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


#TOOLS

@mcp.tool()
def add_task (title: str)-> str:
    tasks= load_tasks()
    new_id= max((t["id"] for t in tasks), default=0) + 1
    new_task = {"id": new_id, "title": title, "done": False}
    tasks.append(new_task)
    save_tasks(tasks)
    return f"Task added with ID: {new_id}"

@mcp.tool()
def list_tasks()-> str:
    tasks = load_tasks()
    if not tasks:
        return "No tasks found."
    lines = []
    for t in tasks:
        mark = "[x]" if t["done"] else "[ ]"
        lines.append(f"{mark} #{t['id']} {t['title']}")
    return "\n".join(lines)


@mcp.tool()
def complete_task(task_id: int) -> str:
    """Mark a task as done using its ID number."""
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = True
            save_tasks(tasks)
            return f"Task #{task_id} marked as done."
    return f"No task found with ID {task_id}."

@mcp.tool()
def delete_task(task_id: int) -> str:
    tasks= load_tasks()
    remaining_task= [t for t in tasks if t["id"] != task_id]
    if len(remaining_task) == len(tasks):
        return f"No task found with ID {task_id}."
    save_tasks(remaining_task)
    return f"Task #{task_id} deleted."


#RESOURCES
@mcp.resource("todo://summary")
def summary() -> str:
    """A quick count of finished and unfinished tasks."""
    tasks = load_tasks()
    done = sum(1 for t in tasks if t["done"])
    return f"Total: {len(tasks)} | Done: {done} | Pending: {len(tasks) - done}"


@mcp.resource("todo://task/{task_id}")
def get_task(task_id: str) -> str:
    """Details of one task by its ID."""
    for t in load_tasks():
        if str(t["id"]) == task_id:
            status = "done" if t["done"] else "pending"
            return f"Task #{t['id']}: {t['title']} ({status})"
    return f"No task found with ID {task_id}."


#PROMPT (message template)

@mcp.prompt()
def plan_my_day(hours_available: str) -> str:
    return (
        f"I have {hours_available} hours today. Look at my to-do list, pick the most important pending tasks, and make a simple schedule."
    )


if __name__ == "__main__":
    mcp.run()