import streamlit as st

from components import (
    st_chessboard,
    initialize_game_state,
    reset_game,
    get_legal_moves,
    is_valid_move,
    make_move,
    get_game_status,
    coordinate_to_position,
    position_to_coordinate,
    validate_coordinate,
    validate_coordinate_with_piece,
    validate_move,
    is_en_passant_move,
    is_castling_move,
    get_castling_type,
    get_captured_pieces_display,
    get_material_advantage,
)

from services.analyzer import analyze_game


def handle_piece_selection(from_coord: str, to_coord: str = None):
    """Handle piece selection and movement."""
    from_valid, from_error = validate_coordinate_with_piece(from_coord, True)
    if not from_valid:
        st.error(from_error)
        return

    from_row, from_col = coordinate_to_position(from_coord)
    piece = st.session_state.chess_board[from_row][from_col]
    current_player = st.session_state.current_player

    if not to_coord:
        st.session_state.selected_square = (from_row, from_col)
        st.session_state.possible_moves = get_legal_moves(
            st.session_state.chess_board, from_row, from_col
        )
        legal_count = len(st.session_state.possible_moves)
        if legal_count > 0:
            st.success(f"Selected {piece} at {from_coord} ({legal_count} legal moves)")
        else:
            st.warning(f"Selected {piece} at {from_coord} (no legal moves available)")
        return

    to_valid, to_error = validate_coordinate(to_coord)
    if not to_valid:
        st.error(to_error)
        return

    to_row, to_col = coordinate_to_position(to_coord)

    legal_moves = get_legal_moves(st.session_state.chess_board, from_row, from_col)
    if (to_row, to_col) in legal_moves:
        move_description = f"Moved {piece} from {from_coord} to {to_coord}"

        if is_en_passant_move(
            st.session_state.chess_board, from_row, from_col, to_row, to_col
        ):
            move_description = (
                f"En passant! {piece} captures from {from_coord} to {to_coord}"
            )
        elif is_castling_move(
            st.session_state.chess_board, from_row, from_col, to_row, to_col
        ):
            castling_type = get_castling_type(from_col, to_col)
            castle_name = "Kingside" if castling_type == "kingside" else "Queenside"
            move_description = (
                f"{castle_name} castling! King moves from {from_coord} to {to_coord}"
            )

        st.session_state.chess_board = make_move(
            st.session_state.chess_board, from_row, from_col, to_row, to_col
        )

        move_notation = f"{from_coord}-{to_coord}"
        st.session_state.move_history.append(move_notation)

        st.session_state.current_player = (
            "black" if current_player == "white" else "white"
        )

        st.session_state.game_status = get_game_status(
            st.session_state.chess_board, st.session_state.current_player
        )

        st.session_state.selected_square = None
        st.session_state.possible_moves = []
        st.session_state.clear_inputs = True

        st.success(move_description)

        if st.session_state.game_status.startswith("checkmate"):
            winner = st.session_state.game_status.split("_")[1]
            st.success(f"Checkmate! {winner.title()} wins!")
        elif st.session_state.game_status == "stalemate":
            st.info("Game ends in stalemate (draw)")
        elif st.session_state.game_status.startswith("check"):
            checked_player = st.session_state.game_status.split("_")[1]
            st.warning(f"{checked_player.title()} is in check!")

    else:
        if is_valid_move(
            st.session_state.chess_board, from_row, from_col, to_row, to_col
        ):
            st.error(f"Move {from_coord} to {to_coord} would put your king in check")
        else:
            st.error(f"Invalid move: {from_coord} to {to_coord}")


def main():
    st.set_page_config(
        page_title="Chess Analyzer",
        page_icon="♟️",
        layout="wide",
    )

    st.title("♟️ Chess Analyzer")

    initialize_game_state()

    if "ai_response" not in st.session_state:
        st.session_state.ai_response = ""

    if st.session_state.game_status == "active":
        st.session_state.game_status = get_game_status(
            st.session_state.chess_board, st.session_state.current_player
        )

    st.sidebar.header("Chessboard Options")
    size = st.sidebar.slider("Board Size", 300, 600, 400, 50)
    board_theme = st.sidebar.selectbox(
        "Board Theme", ["Default", "Dark", "Light", "Mushrooms"]
    )

    with st.sidebar:
        st.subheader("AI Assistant")

        if "ai_question_input" not in st.session_state:
            st.session_state.ai_question_input = ""

        ai_question = st.text_area(
            "Ask the AI a question", 
            placeholder="What is the best move?",
            value=st.session_state.ai_question_input,
            key="ai_question_text_input"
        )

        st.write("**Quick Questions:**")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("What is the best move?", use_container_width=True):
                st.session_state.ai_question_input = "What is the best move in this position?"
                st.rerun()
            if st.button("Analyze position", use_container_width=True):
                st.session_state.ai_question_input = "Please analyze the current position and give me strategic advice."
                st.rerun()

        with col2:
            if st.button("What did I do wrong?", use_container_width=True):
                st.session_state.ai_question_input = "What did I do wrong in my last move? How could I have played better?"
                st.rerun()
            if st.button("Explain this move", use_container_width=True):
                st.session_state.ai_question_input = "Can you explain the chess concept or tactic involved in this position?"
                st.rerun()

        if st.button(
            "Ask AI",
            type="primary",
            use_container_width=True,
            disabled=not ai_question.strip(),
        ):
            if ai_question.strip():
                with st.spinner("Analyzing position..."):
                    try:
                        game_history = (
                            " | ".join(st.session_state.move_history)
                            if st.session_state.move_history
                            else "No moves yet"
                        )

                        selected_piece = ""
                        selected_move = ""
                        if st.session_state.selected_square:
                            row, col = st.session_state.selected_square
                            piece = st.session_state.chess_board[row][col]
                            square_name = position_to_coordinate(row, col)
                            selected_piece = f"{piece} on {square_name}"

                            if st.session_state.possible_moves:
                                moves_list = [
                                    position_to_coordinate(r, c)
                                    for r, c in st.session_state.possible_moves
                                ]
                                selected_move = (
                                    f"Possible moves: {', '.join(moves_list)}"
                                )

                        response = analyze_game(
                            game_history=game_history,
                            selected_piece=selected_piece,
                            selected_move=selected_move,
                            question=ai_question,
                            current_player=st.session_state.current_player,
                            current_board=st.session_state.chess_board,
                        )

                        st.session_state.ai_response = response
                        st.session_state.ai_question_input = ""
                        st.success("Analysis complete!")

                    except Exception as e:
                        st.error(f"Error getting AI response: {str(e)}")
                        st.session_state.ai_response = "Sorry, I couldn't analyze the position right now. Please try again."
            else:
                st.warning("Please enter a question first!")

        st.subheader("AI Response")
        if st.session_state.ai_response:
            st.write(st.session_state.ai_response)
        else:
            st.info("The AI's analysis and recommendations will appear here after you ask a question.")

    col1, col2, col3 = st.columns([1, 5, 1])

    with col1:
        st.subheader("Make a Move")

        clear_inputs = st.session_state.get("clear_inputs", False)
        if clear_inputs:
            st.session_state.clear_inputs = False

        from_coord = (
            st.text_input(
                "From (e.g., e2)",
                placeholder="e2",
                key="from_coord",
                value="" if clear_inputs else st.session_state.get("from_coord", ""),
            )
            .strip()
            .lower()
        )

        game_over = (
            st.session_state.game_status.startswith("checkmate")
            or st.session_state.game_status == "stalemate"
        )

        if from_coord and not game_over:
            from_valid, from_error = validate_coordinate_with_piece(from_coord, True)

            if not from_valid:
                st.error(f"From coordinate: {from_error}")
            else:
                handle_piece_selection(from_coord)
                if st.session_state.possible_moves:
                    moves_str = ", ".join(
                        [
                            position_to_coordinate(r, c)
                            for r, c in st.session_state.possible_moves
                        ]
                    )
                    st.info(f"Legal moves: {moves_str}")
        elif from_coord and game_over:
            st.warning("Game is over! Please reset to continue playing.")

        to_coord = (
            st.text_input(
                "To (e.g., e4)",
                placeholder="e4",
                key="to_coord",
                disabled=not from_coord,
                value="" if clear_inputs else st.session_state.get("to_coord", ""),
            )
            .strip()
            .lower()
        )

        if to_coord and from_coord:
            move_valid, move_error = validate_move(from_coord, to_coord)
            if not move_valid:
                st.error(f"Move validation: {move_error}")
            else:
                st.success(f"Valid move: {from_coord} → {to_coord}")
        elif to_coord:
            to_valid, to_error = validate_coordinate(to_coord)
            if not to_valid:
                st.error(f"To coordinate: {to_error}")

        can_make_move = False
        if not game_over:
            if from_coord and to_coord:
                move_valid, _ = validate_move(from_coord, to_coord)
                can_make_move = move_valid
            elif from_coord:
                from_valid, _ = validate_coordinate_with_piece(from_coord, True)
                can_make_move = from_valid

        if st.button(
            "Make Move", type="primary", disabled=not can_make_move or game_over
        ):
            if from_coord and to_coord:
                handle_piece_selection(from_coord, to_coord)
                st.rerun()
            elif from_coord:
                handle_piece_selection(from_coord)
                st.rerun()
            else:
                st.error("Please enter at least a 'From' coordinate")

    with col2:
        status_col1, status_col2, status_col3 = st.columns([1, 1, 1])

        with status_col1:
            st.write(f"**Current Player:** {st.session_state.current_player.title()}")

        with status_col2:
            status = st.session_state.game_status
            if status.startswith("checkmate"):
                winner = status.split("_")[1]
                st.write(f"**Game Status:** Checkmate - {winner.title()} Wins!")
            elif status == "stalemate":
                st.write("**Game Status:** Stalemate (Draw)")
            elif status.startswith("check"):
                checked_player = status.split("_")[1]
                st.write(f"**Game Status:** {checked_player.title()} in Check")
            else:
                st.write("**Game Status:** Active")

        with status_col3:
            if st.button("Reset Game"):
                reset_game()
                st.rerun()

        st_chessboard(
            board=st.session_state.chess_board,
            size=size,
            board_theme=board_theme,
        )

    with col3:
        st.subheader("Game Information")

        if st.session_state.selected_square:
            row, col = st.session_state.selected_square
            piece = st.session_state.chess_board[row][col]
            square_name = position_to_coordinate(row, col)
            st.write(f"**Selected:** {piece} on {square_name}")
            st.write(f"**Possible moves:** {len(st.session_state.possible_moves)}")

            if st.session_state.possible_moves:
                moves_str = ", ".join(
                    [
                        position_to_coordinate(r, c)
                        for r, c in st.session_state.possible_moves
                    ]
                )
                st.write(f"**Available moves:** {moves_str}")
        else:
            st.write("Enter coordinates to select a piece")

        st.subheader("Captured Pieces")

        white_captures, white_value = get_captured_pieces_display("white")
        if white_captures:
            st.write(f"**White captured:** {white_captures} (Value: {white_value})")
        else:
            st.write("**White captured:** None")

        black_captures, black_value = get_captured_pieces_display("black")
        if black_captures:
            st.write(f"**Black captured:** {black_captures} (Value: {black_value})")
        else:
            st.write("**Black captured:** None")

        advantage_color, advantage_value = get_material_advantage()
        if advantage_value > 0:
            st.write(
                f"**Material advantage:** {advantage_color.title()} +{advantage_value}"
            )
        else:
            st.write("**Material advantage:** Equal")

        st.subheader("Move History")
        if st.session_state.move_history:
            for i, move in enumerate(reversed(st.session_state.move_history[-10:]), 1):
                player = (
                    "White"
                    if (len(st.session_state.move_history) - i) % 2 == 0
                    else "Black"
                )
                st.write(
                    f"{len(st.session_state.move_history) - i + 1}. {player}: {move}"
                )
        else:
            st.write("No moves yet")


if __name__ == "__main__":
    main()
