import streamlit as st

from components import (
    st_chessboard,
    initialize_game_state,
    reset_game,
)


def main():
    st.set_page_config(
        page_title="Chess Analyzer",
        page_icon="♟️",
        layout="wide",
    )

    st.title("♟️ Chess Analyzer")

    initialize_game_state()

    st.sidebar.header("Chessboard Options")

    size = st.sidebar.slider("Board Size", 300, 600, 400, 50)

    board_theme = st.sidebar.selectbox(
        "Board Theme", ["Default", "Dark", "Light", "Mushrooms"]
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        # Game status and controls
        status_col1, status_col2, status_col3 = st.columns([1, 1, 1])

        with status_col1:
            st.write(f"**Current Player:** {st.session_state.current_player.title()}")

        with status_col2:
            st.write(f"**Game Status:** {st.session_state.game_status.title()}")

        with status_col3:
            if st.button("Reset Game"):
                reset_game()
                st.rerun()

        # Render the playable chessboard
        st_chessboard(
            board=st.session_state.chess_board,
            size=size,
            board_theme=board_theme,
        )

    with col2:
        st.subheader("Game Information")

        if st.session_state.selected_square:
            row, col = st.session_state.selected_square
            piece = st.session_state.chess_board[row][col]
            square_name = f"{chr(97 + col)}{8 - row}"
            st.write(f"**Selected:** {piece} on {square_name}")
            st.write(f"**Possible moves:** {len(st.session_state.possible_moves)}")
        else:
            st.write("Click on a piece to select it")

        # Move history
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
