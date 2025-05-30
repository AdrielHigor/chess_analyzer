import streamlit as st
import streamlit.components.v1 as components
from typing import Optional, List, Dict, Any, Tuple
import copy


DEFAULT_BOARD = [
    ["R", "N", "B", "Q", "K", "B", "N", "R"],
    ["P", "P", "P", "P", "P", "P", "P", "P"],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["p", "p", "p", "p", "p", "p", "p", "p"],
    ["r", "n", "b", "q", "k", "b", "n", "r"],
]

PIECE_SYMBOLS = {
    # White pieces
    "K": "♔",
    "Q": "♕",
    "R": "♖",
    "B": "♗",
    "N": "♘",
    "P": "♙",
    # Black pieces
    "k": "♚",
    "q": "♛",
    "r": "♜",
    "b": "♝",
    "n": "♞",
    "p": "♟",
    # Empty square
    "": "",
}

BOARD_THEMES = {
    "Default": {
        "light": "#f0d9b5",
        "dark": "#b58863",
        "border": "#8B4513",
        "light_piece": "#ffffff",
        "dark_piece": "#2c2c2c",
    },
    "Dark": {
        "light": "#4a4a4a",
        "dark": "#2d2d2d",
        "border": "#1a1a1a",
        "light_piece": "#e0e0e0",
        "dark_piece": "#111111",
    },
    "Light": {
        "light": "#ffffff",
        "dark": "#e8e8e8",
        "border": "#cccccc",
        "light_piece": "#666666",
        "dark_piece": "#2c2c2c",
    },
    "Mushrooms": {
        "light": "#0d1117",
        "dark": "#ff00ff",
        "border": "#00ffff",
        "light_piece": "#00ffff",
        "dark_piece": "#1AFF00",
    },
}


def initialize_game_state():
    """Initialize the chess game state in session state."""
    if "chess_board" not in st.session_state:
        st.session_state.chess_board = DEFAULT_BOARD

    if "current_player" not in st.session_state:
        st.session_state.current_player = "white"

    if "selected_square" not in st.session_state:
        st.session_state.selected_square = None

    if "possible_moves" not in st.session_state:
        st.session_state.possible_moves = []

    if "move_history" not in st.session_state:
        st.session_state.move_history = []

    if "game_status" not in st.session_state:
        st.session_state.game_status = "active"


def reset_game():
    """Reset the chess game to initial state."""
    st.session_state.chess_board = DEFAULT_BOARD
    st.session_state.current_player = "white"
    st.session_state.selected_square = None
    st.session_state.possible_moves = []
    st.session_state.move_history = []
    st.session_state.game_status = "active"


def is_white_piece(piece: str) -> bool:
    """Check if a piece is white (uppercase)."""
    return piece.isupper() and piece != ""


def is_black_piece(piece: str) -> bool:
    """Check if a piece is black (lowercase)."""
    return piece.islower() and piece != ""


def is_same_color(piece1: str, piece2: str) -> bool:
    """Check if two pieces are the same color."""
    if not piece1 or not piece2:
        return False
    return (is_white_piece(piece1) and is_white_piece(piece2)) or (
        is_black_piece(piece1) and is_black_piece(piece2)
    )


def get_possible_moves(
    board: List[List[str]], row: int, col: int
) -> List[Tuple[int, int]]:
    """Get all possible moves for a piece at the given position."""
    piece = board[row][col].lower()
    moves = []

    if piece == "p":  # Pawn
        moves = get_pawn_moves(board, row, col)
    elif piece == "r":  # Rook
        moves = get_rook_moves(board, row, col)
    elif piece == "n":  # Knight
        moves = get_knight_moves(board, row, col)
    elif piece == "b":  # Bishop
        moves = get_bishop_moves(board, row, col)
    elif piece == "q":  # Queen
        moves = get_queen_moves(board, row, col)
    elif piece == "k":  # King
        moves = get_king_moves(board, row, col)

    return moves


def get_pawn_moves(board: List[List[str]], row: int, col: int) -> List[Tuple[int, int]]:
    """Get possible moves for a pawn."""
    moves = []
    piece = board[row][col]
    is_white = is_white_piece(piece)

    # Direction: white pawns move up (row decreases), black pawns move down (row increases)
    direction = -1 if is_white else 1
    start_row = 6 if is_white else 1

    # Forward move
    new_row = row + direction
    if 0 <= new_row < 8 and board[new_row][col] == "":
        moves.append((new_row, col))

        # Double move from starting position
        if row == start_row and board[new_row + direction][col] == "":
            moves.append((new_row + direction, col))

    # Diagonal captures
    for dc in [-1, 1]:
        new_row, new_col = row + direction, col + dc
        if 0 <= new_row < 8 and 0 <= new_col < 8:
            target_piece = board[new_row][new_col]
            if target_piece != "" and not is_same_color(piece, target_piece):
                moves.append((new_row, new_col))

    return moves


def get_rook_moves(board: List[List[str]], row: int, col: int) -> List[Tuple[int, int]]:
    """Get possible moves for a rook."""
    moves = []
    piece = board[row][col]

    # Horizontal and vertical directions
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    for dr, dc in directions:
        for i in range(1, 8):
            new_row, new_col = row + dr * i, col + dc * i
            if not (0 <= new_row < 8 and 0 <= new_col < 8):
                break

            target_piece = board[new_row][new_col]
            if target_piece == "":
                moves.append((new_row, new_col))
            elif not is_same_color(piece, target_piece):
                moves.append((new_row, new_col))
                break
            else:
                break

    return moves


def get_knight_moves(
    board: List[List[str]], row: int, col: int
) -> List[Tuple[int, int]]:
    """Get possible moves for a knight."""
    moves = []
    piece = board[row][col]

    # Knight moves in L-shape
    knight_moves = [
        (-2, -1),
        (-2, 1),
        (-1, -2),
        (-1, 2),
        (1, -2),
        (1, 2),
        (2, -1),
        (2, 1),
    ]

    for dr, dc in knight_moves:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < 8 and 0 <= new_col < 8:
            target_piece = board[new_row][new_col]
            if target_piece == "" or not is_same_color(piece, target_piece):
                moves.append((new_row, new_col))

    return moves


def get_bishop_moves(
    board: List[List[str]], row: int, col: int
) -> List[Tuple[int, int]]:
    """Get possible moves for a bishop."""
    moves = []
    piece = board[row][col]

    # Diagonal directions
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    for dr, dc in directions:
        for i in range(1, 8):
            new_row, new_col = row + dr * i, col + dc * i
            if not (0 <= new_row < 8 and 0 <= new_col < 8):
                break

            target_piece = board[new_row][new_col]
            if target_piece == "":
                moves.append((new_row, new_col))
            elif not is_same_color(piece, target_piece):
                moves.append((new_row, new_col))
                break
            else:
                break

    return moves


def get_queen_moves(
    board: List[List[str]], row: int, col: int
) -> List[Tuple[int, int]]:
    """Get possible moves for a queen (combination of rook and bishop)."""
    return get_rook_moves(board, row, col) + get_bishop_moves(board, row, col)


def get_king_moves(board: List[List[str]], row: int, col: int) -> List[Tuple[int, int]]:
    """Get possible moves for a king."""
    moves = []
    piece = board[row][col]

    # King moves one square in any direction
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    for dr, dc in directions:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < 8 and 0 <= new_col < 8:
            target_piece = board[new_row][new_col]
            if target_piece == "" or not is_same_color(piece, target_piece):
                moves.append((new_row, new_col))

    return moves


def is_valid_move(
    board: List[List[str]], from_row: int, from_col: int, to_row: int, to_col: int
) -> bool:
    """Check if a move is valid."""
    if not (
        0 <= from_row < 8 and 0 <= from_col < 8 and 0 <= to_row < 8 and 0 <= to_col < 8
    ):
        return False

    piece = board[from_row][from_col]
    if piece == "":
        return False

    possible_moves = get_possible_moves(board, from_row, from_col)
    return (to_row, to_col) in possible_moves


def make_move(
    board: List[List[str]], from_row: int, from_col: int, to_row: int, to_col: int
) -> List[List[str]]:
    """Make a move on the board and return the new board state."""
    new_board = copy.deepcopy(board)
    piece = new_board[from_row][from_col]
    new_board[to_row][to_col] = piece
    new_board[from_row][from_col] = ""
    return new_board


def get_square_color(board_theme: str, square_class: str) -> str:
    """Get the color of a square based on the board theme."""
    return BOARD_THEMES[board_theme][square_class]


def populate_square_html(
    piece: str,
    board_theme: str,
    row_idx: int,
    col_idx: int,
    key: str,
    size: int = 400,
) -> str:
    """Populate the HTML for a square."""
    selected_square = st.session_state.selected_square
    possible_moves = st.session_state.possible_moves

    piece_symbol = PIECE_SYMBOLS.get(piece, piece)
    square_class = "light" if (row_idx + col_idx) % 2 == 0 else "dark"
    square_id = f"square-{key}-{row_idx}-{col_idx}"

    # Determine square styling based on game state
    base_color = (
        get_square_color(board_theme, "light")
        if square_class == "light"
        else get_square_color(board_theme, "dark")
    )
    square_color = base_color

    # Highlight selected square
    if selected_square and selected_square == (row_idx, col_idx):
        square_color = get_square_color(
            board_theme, "light"
        )  # Yellow for selected square

    # Highlight possible moves
    elif possible_moves and (row_idx, col_idx) in possible_moves:
        if piece == "":
            square_color = get_square_color(
                board_theme, "light"
            )  # Light green for empty squares
        else:
            square_color = get_square_color(
                board_theme, "dark"
            )  # Light pink for capture squares

    return f"""
    <div id="{square_id}" 
            class="square {square_class}" 
            onclick="handleSquareClick_{key}({row_idx}, {col_idx})"
            style="
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: {size//12}px;
            font-weight: bold;
            color: {get_square_color(board_theme, "light_piece") if is_white_piece(piece) else get_square_color(board_theme, "dark_piece")};
            width: {size//8}px;
            height: {size//8}px;
            background-color: {square_color};
            transition: background-color 0.2s;
            cursor: pointer;
            border: 2px solid transparent;
            "
            onmouseover="this.style.opacity='0.8'"
            onmouseout="this.style.opacity='1'">
        {piece_symbol}
    </div>
    """


def st_chessboard(
    board: Optional[List[List[str]]] = DEFAULT_BOARD,
    size: int = 400,
    key: Optional[str] = "playable_chessboard",
    board_theme: str = "Default",
) -> Optional[Dict[str, Any]]:
    """
    Create an interactive chessboard component.

    Parameters:
    -----------
    board : List[List[str]], optional
        8x8 matrix representing the chess board. If None, creates standard starting position.
        Use standard chess notation: K=King, Q=Queen, R=Rook, B=Bishop, N=Knight, P=Pawn
        Uppercase for white pieces, lowercase for black pieces, empty string for empty squares.

    size : int, default 400
        Size of the chessboard in pixels

    key : str, optional
        Unique key for the component (used for HTML element IDs)

    board_theme : str, default "Default"
        Theme of the chessboard ("Default", "Dark", "Light", "Mushrooms")

    Returns:
    --------
    Dict with clicked square information if interactive=True, None otherwise
    """

    # Create the HTML/CSS/JS for the chessboard
    html_content = f"""
    <div id="chessboard-container-{key}" style="display: flex; justify-content: center; margin: 20px 0;">
        <div id="chessboard-{key}" style="
            display: grid;
            grid-template-columns: repeat(8, {size//8}px);
            grid-template-rows: repeat(8, {size//8}px);
            gap: 0;
            border: 3px solid #8B4513;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            background: #8B4513;
        ">
    """

    # Generate squares
    for row_idx in range(8):
        for col_idx in range(8):
            html_content += populate_square_html(
                board[row_idx][col_idx],
                board_theme,
                row_idx,
                col_idx,
                key,
                size,
            )

    html_content += "</div></div>"

    # Add JavaScript for interactivity
    board_json = str(board).replace("'", '"')

    html_content += f"""
    <script>
    function handleSquareClick_{key}(row, col) {{
        const board = {board_json};
        const data = {{
            'row': row,
            'col': col,
            'square': String.fromCharCode(97 + col) + (8 - row),
            'piece': board[row] && board[row][col] ? board[row][col] : '',
            'component_key': '{key}',
            'current_player': '{st.session_state.current_player}'
        }};
        
        // Send data back to Streamlit
        window.parent.postMessage({{
            type: 'streamlit:componentValue',
            value: data
        }}, '*');
    }}
    </script>
    """

    return components.html(html_content, height=size + 100)
