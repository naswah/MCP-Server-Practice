import json
import random
from pathlib import Path
from mcp.server.mcpserver import MCPServer

mcp= MCPServer("Flashcard")
FILE= Path(__file__).parent / "flashcards.json"

def load_cards()->list:
    if FILE.exists() and FILE.read_text(encoding="utf-8").strip():
        return json.loads(FILE.read_text(encoding="utf-8"))
    return []

def save_cards(cards: list)-> None:
    FILE.write_text(json.dumps(cards, indent=2), encoding="utf-8")

@mcp.tool()
def add_card(question: str, answer: str)-> str:
    cards= load_cards()
    cards.append({"question" : question, "answer": answer})
    save_cards(cards)
    return f"Card added: {question}"

@mcp.tool()
def list_cards()-> str:
    cards= load_cards()
    if not cards:
        return "No flashcards found."
    lines= []
    for i, card in enumerate(cards, start=1):
        lines.append(f"#{i} Q: {card['question']} A: {card['answer']}")
    return "\n".join(lines)

@mcp.tool()
def random_question()-> str:
    cards= load_cards()
    if not cards:
        return "No flashcards available."
    return random.choice(cards)["question"]

@mcp.tool()
def check_answer(question: str, my_answer: str)-> str:
    for c in load_cards():
        if c["question"] == question:
            if my_answer.strip().lower() == c["answer"].strip().lower():
                return "Correct!"
            else:
                return f"Incorrect. The correct answer is: {c['answer']}"
    return "I could not find the question!"


@mcp.resource("cards://count")
def card_count()-> str:
    """Return the total number of flashcards."""
    return str(len(load_cards()))

@mcp.prompt()
def quiz_me(number_of_questions: str)-> str:
    return (
        f"Quiz me with {number_of_questions} flashcard questions. Use random_question to ask one at a time, wait for my answer, check it with check_answer, and give me my score at the end."
    )

if __name__=="__main__":
    mcp.run()