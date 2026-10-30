# MCP Learning Projects

Small Python projects I built while learning the Model Context Protocol (MCP). 
Each server exposes **tools**, **resources**, and **prompts** that AI apps like Claude can use.

## Projects

- **study-helper** (`server.py`): add numbers, count words, read notes by topic, and a "explain simply" prompt.
- **todo-helper** (`todo_server.py`): add, list, complete, and delete tasks, saved in `tasks.json`.
- **flash-card** (`flashcard_server.py`): Add question, answers and check the know (quiz) from flashcards, save the flashcards as `flashcards.json`
- **study_buddy** (`study_buddy.py`): Helps to create notes for multiple subjects along with the til; and descrption, search the notes as per theor keywords and quiz the random questions from the note itself.

## Setup

    python -m venv venv
    venv\Scripts\activate
    pip install "mcp[cli]"

Requires Python 3.10+ and the MCP Python SDK v2 (`MCPServer`).

## Run and test

    mcp dev todo_server.py

This opens the MCP Inspector in your browser (needs Node.js).

## Use with Claude Desktop

Add this to your Claude Desktop config, using the full path to your file:

    {
      "mcpServers": {
        "todo-helper": {
          "command": "python",
          "args": ["C:/full/path/to/todo_server.py"]
        }
      }
    }

## What I learned

Check Theory.txt for notes, main points:

- Tools = actions, resources = data, prompts = templates
- Fixed resources vs resource templates (`{placeholder}`)
- Never use `print()` in stdio servers