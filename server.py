from mcp.server.mcpserver import MCPServer

mcp= MCPServer("study-helper")

@mcp.tool()
def add_numbers (a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

@mcp.tool()
def word_count(text: str) -> int:
    """Count the number of words in a given text."""
    return len(text.split())

@mcp.resource("notes://{topic}")
def get_notes(topic: str)-> str:
    """Retrieve notes for a specific topic."""
    return f"Notes for {topic}: [This is where the notes would be displayed.]"

@mcp.resource("notes://welcome")
def welcome() -> str:
    """A fixed welcome note."""
    return "Welcome to my study helper!"

@mcp.prompt()
def explain_simply(concept: str)-> str:
    return f" Explain {concept} to a 10 year old in simple language and terms using one example. Make it fun and engaging."

if __name__ == "__main__":
    mcp.run()