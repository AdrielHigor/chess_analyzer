import os
from typing import List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def analyze_game(
    game_history: str,
    selected_piece: str,
    selected_move: str,
    question: str,
    current_player: str,
    current_board: List[List[str]],
) -> str:
    """Analyze the game history and return a summary of the game."""
    if not OPENAI_API_KEY:
        return "Please set your OPENAI_API_KEY environment variable to use the AI assistant."

    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""You are a chess expert analyzing a chess position. Please provide helpful analysis and advice.

Use markdown to format your response.
Use bold to highlight important points.
Use italic to highlight chess concepts.
Use code blocks to format chess moves.

The BOARD structure is a 8x8 matrix of strings. The strings are the pieces on the board. The empty squares are represented by an empty string. The pieces are represented by the following characters:
- r: black rook
- n: black knight
- b: black bishop
- q: black queen
- k: black king
- p: black pawn
- : empty square
- R: white rook
- N: white knight
- B: white bishop
- Q: white queen
- K: white king
- P: white pawn

The board is as follows:
[
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p", "p", "p", "p", "p", "p", "p", "p"],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["P", "P", "P", "P", "P", "P", "P", "P"],
    ["R", "N", "B", "Q", "K", "B", "N", "R"],
]

To describe proposed moves, use as example the following format:
- "Move from e2 to e4"
- "Capture black pawn using en passant from e4 to e5"
- "Castle kingside from e1 to g1"
- "Castle queenside from e1 to c1"
- "Promotion to queen from e7 to e8"

Current Player: {current_player}
Game History: {game_history} (If there is no game history, say "No moves yet")
Selected Piece: {selected_piece}
Available Moves: {selected_move}
Current Board: {current_board}

Question: {question}

Please provide a clear, detailed analysis focusing on:
1. The current position evaluation (evaluate the position from the perspective of the current player, be direct to the point with your analysis, no need to describe the board in details, use the move history to analyze only the most recent moves make this evaluation short and concise)
2. Strategic considerations (if the user asks for strategic advices, moves recomendations or tactical opportunities, provide them)
3. Educational insights about chess concepts involved (if applicable, highlight if the move is book moves, book moves are well known chess positions, mention the name of the book move if applicable or chess concepts based on the current board)

Keep response under 150 words. Be direct and practical."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}. Please check your API key and try again."
