import streamlit as st
import streamlit.components.v1 as components
from typing import Optional, List, Dict, Any, Tuple
import copy


DEFAULT_BOARD = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p", "p", "p", "p", "p", "p", "p", "p"],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["P", "P", "P", "P", "P", "P", "P", "P"],
    ["R", "N", "B", "Q", "K", "B", "N", "R"],
]

PIECE_SYMBOLS = {
    "K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙",
    "k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟", "": "",
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


def coordinate_to_position(coordinate: str) -> tuple[int, int]:
    """Convert chess coordinate (e.g., 'a1') to (row, col) indices."""
    if len(coordinate) != 2:
        raise ValueError("Coordinate must be 2 characters (e.g., 'a1')")
    
    col = ord(coordinate[0].lower()) - ord("a")
    row = 8 - int(coordinate[1])
    
    if not (0 <= col < 8 and 0 <= row < 8):
        raise ValueError("Invalid coordinate")
    
    return row, col


def position_to_coordinate(row: int, col: int) -> str:
    """Convert (row, col) indices to chess coordinate."""
    return f"{chr(97 + col)}{8 - row}"


def validate_coordinate(coordinate: str) -> tuple[bool, str]:
    """Validate a chess coordinate and return (is_valid, error_message)."""
    if not coordinate:
        return True, ""
    
    if len(coordinate) != 2:
        return False, "Coordinate must be 2 characters (e.g., 'e2')"
    
    if not coordinate[0].lower().isalpha():
        return False, "First character must be a letter (a-h)"
    
    if not coordinate[1].isdigit():
        return False, "Second character must be a number (1-8)"
    
    try:
        coordinate_to_position(coordinate)
        return True, ""
    except ValueError as e:
        return False, str(e)


def validate_coordinate_with_piece(coordinate: str, check_piece: bool = False) -> tuple[bool, str]:
    """Validate a chess coordinate and optionally check if there's a piece there."""
    if not coordinate:
        return True, ""
    
    is_valid, error_msg = validate_coordinate(coordinate)
    if not is_valid:
        return False, error_msg
    
    if check_piece:
        try:
            row, col = coordinate_to_position(coordinate)
            piece = st.session_state.chess_board[row][col]
            if not piece:
                return False, f"No piece at {coordinate}"
            
            current_player = st.session_state.current_player
            if current_player == "white" and not is_white_piece(piece):
                return False, f"It's white's turn - {coordinate} has a black piece"
            elif current_player == "black" and not is_black_piece(piece):
                return False, f"It's black's turn - {coordinate} has a white piece"
        except (IndexError, KeyError):
            return False, "Invalid board position"
    
    return True, ""


def validate_move(from_coord: str, to_coord: str) -> tuple[bool, str]:
    """Validate a complete move from one coordinate to another."""
    from_valid, from_error = validate_coordinate_with_piece(from_coord, True)
    if not from_valid:
        return False, from_error
    
    to_valid, to_error = validate_coordinate(to_coord)
    if not to_valid:
        return False, to_error
    
    try:
        from_row, from_col = coordinate_to_position(from_coord)
        to_row, to_col = coordinate_to_position(to_coord)
        
        legal_moves = get_legal_moves(st.session_state.chess_board, from_row, from_col)
        if (to_row, to_col) in legal_moves:
            return True, ""
        else:
            piece = st.session_state.chess_board[from_row][from_col]
            if is_valid_move(st.session_state.chess_board, from_row, from_col, to_row, to_col):
                return False, f"Move {from_coord} to {to_coord} would put your king in check"
            else:
                return False, f"{piece} cannot move from {from_coord} to {to_coord}"
    except Exception as e:
        return False, f"Error validating move: {str(e)}"


def initialize_game_state():
    """Initialize the chess game state in session state."""
    if "chess_board" not in st.session_state:
        st.session_state.chess_board = copy.deepcopy(DEFAULT_BOARD)

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

    # Additional state for special moves
    if "last_move" not in st.session_state:
        st.session_state.last_move = None  # For en passant

    if "king_moved" not in st.session_state:
        st.session_state.king_moved = {"white": False, "black": False}

    if "rook_moved" not in st.session_state:
        st.session_state.rook_moved = {
            "white": {"kingside": False, "queenside": False},
            "black": {"kingside": False, "queenside": False}
        }
    
    if "captured_pieces" not in st.session_state:
        st.session_state.captured_pieces = {
            "white": [],
            "black": []
        }


def reset_game():
    """Reset the chess game to initial state."""
    st.session_state.chess_board = copy.deepcopy(DEFAULT_BOARD)
    st.session_state.current_player = "white"
    st.session_state.selected_square = None
    st.session_state.possible_moves = []
    st.session_state.move_history = []
    st.session_state.game_status = get_game_status(st.session_state.chess_board, "white")
    st.session_state.last_move = None
    st.session_state.king_moved = {"white": False, "black": False}
    st.session_state.rook_moved = {
        "white": {"kingside": False, "queenside": False},
        "black": {"kingside": False, "queenside": False}
    }
    st.session_state.captured_pieces = {
        "white": [],
        "black": []
    }


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


def get_basic_king_moves(board: List[List[str]], row: int, col: int) -> List[Tuple[int, int]]:
    """Get basic king moves (one square in any direction) without castling."""
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


def get_possible_moves(
    board: List[List[str]], row: int, col: int, include_castling: bool = True
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
        if include_castling:
            moves = get_king_moves(board, row, col)
        else:
            moves = get_basic_king_moves(board, row, col)

    return moves


def get_pawn_moves(board: List[List[str]], row: int, col: int) -> List[Tuple[int, int]]:
    """Get possible moves for a pawn, including en passant."""
    moves = []
    piece = board[row][col]
    is_white = is_white_piece(piece)

    # Direction: white pawns move up (row decreases), black pawns move down (row increases)
    direction = -1 if is_white else 1
    # White pawns start at row 6 (rank 2), black pawns start at row 1 (rank 7)
    start_row = 6 if is_white else 1

    # Forward move
    new_row = row + direction
    if 0 <= new_row < 8 and board[new_row][col] == "":
        moves.append((new_row, col))

        # Double move from starting position
        if row == start_row and 0 <= new_row + direction < 8 and board[new_row + direction][col] == "":
            moves.append((new_row + direction, col))

    # Diagonal captures
    for dc in [-1, 1]:
        new_row, new_col = row + direction, col + dc
        if 0 <= new_row < 8 and 0 <= new_col < 8:
            target_piece = board[new_row][new_col]
            if target_piece != "" and not is_same_color(piece, target_piece):
                moves.append((new_row, new_col))

    # En passant capture
    if hasattr(st.session_state, 'last_move') and st.session_state.last_move:
        last_move = st.session_state.last_move
        # Check if last move was a pawn moving two squares
        if (last_move['piece'].lower() == 'p' and 
            abs(last_move['to_row'] - last_move['from_row']) == 2):
            
            # Check if we're on the correct rank for en passant
            en_passant_rank = 3 if is_white else 4  # 5th rank for white, 4th rank for black
            
            if row == en_passant_rank:
                # Check if the last moved pawn is adjacent to our pawn
                if (last_move['to_row'] == row and 
                    abs(last_move['to_col'] - col) == 1):
                    
                    # The en passant capture square is behind the opponent's pawn
                    capture_row = last_move['to_row'] + direction
                    capture_col = last_move['to_col']
                    
                    if 0 <= capture_row < 8:
                        moves.append((capture_row, capture_col))

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
    """Get possible moves for a king, including castling."""
    moves = []
    piece = board[row][col]
    is_white = is_white_piece(piece)
    color = "white" if is_white else "black"

    # King moves one square in any direction
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    for dr, dc in directions:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < 8 and 0 <= new_col < 8:
            target_piece = board[new_row][new_col]
            if target_piece == "" or not is_same_color(piece, target_piece):
                moves.append((new_row, new_col))

    # Castling logic
    if (hasattr(st.session_state, 'king_moved') and 
        hasattr(st.session_state, 'rook_moved') and
        not st.session_state.king_moved.get(color, False)):
        
        # King must be on starting square
        starting_row = 7 if is_white else 0
        if row == starting_row and col == 4:  # King on e1 or e8
            
            # Check if king is in check (can't castle out of check)
            if not is_in_check(board, color):
                
                # Kingside castling (short castling)
                if not st.session_state.rook_moved.get(color, {}).get("kingside", False):
                    # Check if rook is on h1/h8
                    if board[starting_row][7].lower() == 'r' and is_same_color(piece, board[starting_row][7]):
                        # Check if squares between king and rook are empty
                        if board[starting_row][5] == "" and board[starting_row][6] == "":
                            # Check if king passes through check
                            if (not is_square_attacked(board, starting_row, 5, "black" if is_white else "white") and
                                not is_square_attacked(board, starting_row, 6, "black" if is_white else "white")):
                                moves.append((starting_row, 6))  # King moves to g1/g8
                
                # Queenside castling (long castling)
                if not st.session_state.rook_moved.get(color, {}).get("queenside", False):
                    # Check if rook is on a1/a8
                    if board[starting_row][0].lower() == 'r' and is_same_color(piece, board[starting_row][0]):
                        # Check if squares between king and rook are empty
                        if (board[starting_row][1] == "" and 
                            board[starting_row][2] == "" and 
                            board[starting_row][3] == ""):
                            # Check if king passes through check
                            if (not is_square_attacked(board, starting_row, 2, "black" if is_white else "white") and
                                not is_square_attacked(board, starting_row, 3, "black" if is_white else "white")):
                                moves.append((starting_row, 2))  # King moves to c1/c8

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
    """Make a move on the board and return the new board state. Handles special moves."""
    new_board = copy.deepcopy(board)
    piece = new_board[from_row][from_col]
    piece_lower = piece.lower()
    is_white = is_white_piece(piece)
    color = "white" if is_white else "black"
    
    # Check for captures before making the move
    captured_piece = new_board[to_row][to_col]
    
    # Check for en passant before making the standard move
    is_en_passant = False
    en_passant_captured_piece = None
    if piece_lower == 'p' and abs(to_col - from_col) == 1 and new_board[to_row][to_col] == "":
        # This is a diagonal pawn move to an empty square - check if it's en passant
        if (hasattr(st.session_state, 'last_move') and 
            st.session_state.last_move and
            st.session_state.last_move['piece'].lower() == 'p' and
            abs(st.session_state.last_move['to_row'] - st.session_state.last_move['from_row']) == 2 and
            st.session_state.last_move['to_col'] == to_col and
            st.session_state.last_move['to_row'] == from_row):
            is_en_passant = True
            en_passant_captured_piece = new_board[from_row][to_col]
    
    # Standard move
    new_board[to_row][to_col] = piece
    new_board[from_row][from_col] = ""
    
    # Handle special moves
    
    # En passant capture - remove the captured pawn
    if is_en_passant:
        new_board[from_row][to_col] = ""
    
    # Castling
    if piece_lower == 'k' and abs(to_col - from_col) == 2:
        # This is a castling move
        if to_col == 6:  # Kingside castling
            # Move the rook from h-file to f-file
            rook_from_col = 7
            rook_to_col = 5
        else:  # Queenside castling (to_col == 2)
            # Move the rook from a-file to d-file
            rook_from_col = 0
            rook_to_col = 3
        
        # Move the rook
        rook = new_board[from_row][rook_from_col]
        new_board[from_row][rook_to_col] = rook
        new_board[from_row][rook_from_col] = ""
    
    # Track captured pieces
    if hasattr(st.session_state, 'captured_pieces'):
        if captured_piece != "":
            # Regular capture
            st.session_state.captured_pieces[color].append(captured_piece)
        elif is_en_passant and en_passant_captured_piece:
            # En passant capture
            st.session_state.captured_pieces[color].append(en_passant_captured_piece)
    
    # Track piece movements for castling rights
    if hasattr(st.session_state, 'king_moved') and hasattr(st.session_state, 'rook_moved'):
        # Track king movement
        if piece_lower == 'k':
            st.session_state.king_moved[color] = True
        
        # Track rook movement
        if piece_lower == 'r':
            # Determine which rook moved
            if from_col == 0:  # Queenside rook
                st.session_state.rook_moved[color]["queenside"] = True
            elif from_col == 7:  # Kingside rook
                st.session_state.rook_moved[color]["kingside"] = True
    
    # Store last move for en passant
    if hasattr(st.session_state, 'last_move'):
        st.session_state.last_move = {
            'piece': piece,
            'from_row': from_row,
            'from_col': from_col,
            'to_row': to_row,
            'to_col': to_col
        }
    
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

    base_color = (
        get_square_color(board_theme, "light")
        if square_class == "light"
        else get_square_color(board_theme, "dark")
    )
    square_color = base_color

    destination_square = None
    if hasattr(st.session_state, 'to_coord') and st.session_state.to_coord:
        try:
            to_coord = st.session_state.to_coord.strip().lower()
            if to_coord:
                is_valid, _ = validate_coordinate(to_coord)
                if is_valid:
                    dest_row, dest_col = coordinate_to_position(to_coord)
                    destination_square = (dest_row, dest_col)
        except:
            destination_square = None

    if selected_square and selected_square == (row_idx, col_idx):
        square_color = "#ffff99"

    elif destination_square and destination_square == (row_idx, col_idx):
        square_color = "#87ceeb"

    elif possible_moves and (row_idx, col_idx) in possible_moves:
        if piece == "":
            square_color = "#90ee90"
        else:
            square_color = "#ffb6c1"

    return f"""
    <div id="{square_id}" 
            class="square {square_class}" 
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
            border: 2px solid transparent;
            ">
        {piece_symbol}
    </div>
    """


def st_chessboard(
    board: Optional[List[List[str]]] = DEFAULT_BOARD,
    size: int = 400,
    key: Optional[str] = "playable_chessboard",
    board_theme: str = "Default",
) -> Optional[Dict[str, Any]]:
    """Create an interactive chessboard component."""

    square_size = size // 8
    coord_size = square_size // 2

    html_content = f"""
    <div id="chessboard-container-{key}" style="display: flex; justify-content: center; margin: 20px 0;">
        <div style="display: flex; flex-direction: column; align-items: center;">
            
            <div style="display: flex; margin-bottom: 5px;">
                <div style="width: {coord_size}px;"></div> 
                {''.join([f'<div style="width: {square_size}px; height: {coord_size}px; display: flex; align-items: center; justify-content: center; font-size: {coord_size//2}px; font-weight: bold; color: #ffffff;">{chr(97 + i)}</div>' for i in range(8)])}
            </div>
            
            <div style="display: flex;">
                <div style="display: flex; flex-direction: column; margin-right: 5px;">
                    {''.join([f'<div style="width: {coord_size}px; height: {square_size}px; display: flex; align-items: center; justify-content: center; font-size: {coord_size//2}px; font-weight: bold; color: #ffffff;">{8 - i}</div>' for i in range(8)])}
                </div>
                
                <div id="chessboard-{key}" style="
                    display: grid;
                    grid-template-columns: repeat(8, {square_size}px);
                    grid-template-rows: repeat(8, {square_size}px);
                    gap: 0;
                    border: 3px solid #8B4513;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                    background: #8B4513;
                ">
    """

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

    html_content += """
                </div>
            </div>
        </div>
    </div>
    """

    return components.html(html_content, height=size + 150)


def get_king_position(board: List[List[str]], color: str) -> Optional[Tuple[int, int]]:
    """Find the position of the king for the given color."""
    king_piece = "K" if color == "white" else "k"
    
    for row in range(8):
        for col in range(8):
            if board[row][col] == king_piece:
                return (row, col)
    
    return None


def is_square_attacked(board: List[List[str]], row: int, col: int, by_color: str) -> bool:
    """Check if a square is attacked by any piece of the given color."""
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == "":
                continue
                
            piece_color = "white" if is_white_piece(piece) else "black"
            if piece_color != by_color:
                continue
                
            # Use non-castling moves to prevent recursion
            possible_moves = get_possible_moves(board, r, c, include_castling=False)
            if (row, col) in possible_moves:
                return True
    
    return False


def is_in_check(board: List[List[str]], color: str) -> bool:
    """Check if the king of the given color is in check."""
    king_pos = get_king_position(board, color)
    if not king_pos:
        return False
    
    opponent_color = "black" if color == "white" else "white"
    return is_square_attacked(board, king_pos[0], king_pos[1], opponent_color)


def would_be_in_check(board: List[List[str]], from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
    """Check if making a move would leave the current player's king in check."""
    moving_piece = board[from_row][from_col]
    if not moving_piece:
        return True
    
    player_color = "white" if is_white_piece(moving_piece) else "black"
    
    temp_board = copy.deepcopy(board)
    temp_board[to_row][to_col] = temp_board[from_row][from_col]
    temp_board[from_row][from_col] = ""
    
    return is_in_check(temp_board, player_color)


def get_legal_moves(board: List[List[str]], row: int, col: int) -> List[Tuple[int, int]]:
    """Get all legal moves for a piece (excluding moves that would put own king in check)."""
    possible_moves = get_possible_moves(board, row, col, include_castling=True)
    legal_moves = []
    
    for to_row, to_col in possible_moves:
        if not would_be_in_check(board, row, col, to_row, to_col):
            legal_moves.append((to_row, to_col))
    
    return legal_moves


def has_legal_moves(board: List[List[str]], color: str) -> bool:
    """Check if the given color has any legal moves."""
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece == "":
                continue
                
            piece_color = "white" if is_white_piece(piece) else "black"
            if piece_color != color:
                continue
                
            legal_moves = get_legal_moves(board, row, col)
            if legal_moves:
                return True
    
    return False


def is_checkmate(board: List[List[str]], color: str) -> bool:
    """Check if the given color is in checkmate."""
    return is_in_check(board, color) and not has_legal_moves(board, color)


def is_stalemate(board: List[List[str]], color: str) -> bool:
    """Check if the given color is in stalemate."""
    return not is_in_check(board, color) and not has_legal_moves(board, color)


def get_game_status(board: List[List[str]], current_player: str) -> str:
    """Get the current game status."""
    if is_checkmate(board, current_player):
        winner = "black" if current_player == "white" else "white"
        return f"checkmate_{winner}_wins"
    elif is_stalemate(board, current_player):
        return "stalemate"
    elif is_in_check(board, current_player):
        return f"check_{current_player}"
    else:
        return "active"


def is_en_passant_move(board: List[List[str]], from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
    """Check if a move is an en passant capture."""
    piece = board[from_row][from_col]
    if piece.lower() != 'p':
        return False
    
    # Must be a diagonal move to an empty square
    if abs(to_col - from_col) != 1 or board[to_row][to_col] != "":
        return False
    
    # Check if last move enables en passant
    if not (hasattr(st.session_state, 'last_move') and st.session_state.last_move):
        return False
    
    last_move = st.session_state.last_move
    return (last_move['piece'].lower() == 'p' and
            abs(last_move['to_row'] - last_move['from_row']) == 2 and
            last_move['to_col'] == to_col and
            last_move['to_row'] == from_row)


def is_castling_move(board: List[List[str]], from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
    """Check if a move is a castling move."""
    piece = board[from_row][from_col]
    if piece.lower() != 'k':
        return False
    
    # King must move exactly 2 squares horizontally
    return from_row == to_row and abs(to_col - from_col) == 2


def get_castling_type(from_col: int, to_col: int) -> str:
    """Get the type of castling move."""
    if to_col == 6:
        return "kingside"
    elif to_col == 2:
        return "queenside"
    return ""


def get_captured_pieces_display(color: str) -> tuple[str, int]:
    """Get captured pieces for display, returning (formatted_string, total_value)."""
    if not hasattr(st.session_state, 'captured_pieces'):
        return "", 0
    
    captured = st.session_state.captured_pieces.get(color, [])
    if not captured:
        return "", 0
    
    piece_values = {
        'p': 1, 'P': 1,  # Pawn
        'n': 3, 'N': 3,  # Knight
        'b': 3, 'B': 3,  # Bishop
        'r': 5, 'R': 5,  # Rook
        'q': 9, 'Q': 9,  # Queen
        'k': 0, 'K': 0   # King (shouldn't be captured, but just in case)
    }
    
    captured_sorted = sorted(captured, key=lambda p: piece_values.get(p, 0), reverse=True)
    
    display_pieces = [PIECE_SYMBOLS.get(piece, piece) for piece in captured_sorted]
    
    total_value = sum(piece_values.get(piece, 0) for piece in captured)
    
    return " ".join(display_pieces), total_value


def get_material_advantage() -> tuple[str, int]:
    """Get material advantage information."""
    if not hasattr(st.session_state, 'captured_pieces'):
        return "", 0
    
    _, white_captured_value = get_captured_pieces_display("white")
    _, black_captured_value = get_captured_pieces_display("black")
    
    advantage = white_captured_value - black_captured_value
    
    if advantage > 0:
        return "white", advantage
    elif advantage < 0:
        return "black", abs(advantage)
    else:
        return "", 0
