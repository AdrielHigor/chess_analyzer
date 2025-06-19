# Chess Analyzer

## Overview

The Chess Analyzer project was created to demo the capabilities of Streamlit by building a fully interactive chess game with AI-powered analysis. This application combines a custom-built chess engine with OpenAI's GPT models to provide real-time game analysis, move suggestions, and educational insights.

## Features

### 🎮 Interactive Chess Gameplay
- **Full Chess Implementation**: Complete rule validation including castling, en passant, pawn promotion
- **Visual Chess Board**: Custom HTML/CSS chess board with multiple themes
- **Move Validation**: Real-time validation of legal moves and check/checkmate detection
- **Game State Management**: Track move history, captured pieces, and material advantage

### 🤖 AI-Powered Analysis
- **Position Evaluation**: Get AI analysis of current board positions
- **Move Recommendations**: Ask for the best moves in any position
- **Strategic Insights**: Learn about chess concepts and tactics
- **Educational Feedback**: Understand mistakes and improvements

### 🎨 Customization Options
- **Multiple Board Themes**: Default, Dark, Light, and Mushrooms themes
- **Adjustable Board Size**: Customize board size from 300-600 pixels
- **Responsive Layout**: Three-column layout optimized for different screen sizes

### 📊 Game Analytics
- **Move History**: Complete record of all moves played
- **Captured Pieces Display**: Visual representation of captured pieces
- **Material Advantage**: Real-time calculation of material balance
- **Game Status Tracking**: Check, checkmate, and stalemate detection

## Installation

### Prerequisites
- Python 3.8 or higher
- OpenAI API key (for AI analysis features)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chess_analyzer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file in the project root:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

## Usage

### Playing Chess
1. **Making Moves**: Enter coordinates in the "From" field (e.g., "e2") to select a piece
2. **View Legal Moves**: Available moves will be highlighted on the board
3. **Complete Move**: Enter the destination in the "To" field (e.g., "e4")
4. **Game Status**: Current player, check status, and game outcome are displayed

### AI Assistant
1. **Ask Questions**: Use the sidebar AI assistant to ask about positions
2. **Quick Questions**: Use preset buttons for common queries
3. **Custom Analysis**: Type specific questions about moves or strategies
4. **Educational Insights**: Learn about chess concepts and tactical patterns

### Coordinate System
- **Files**: a-h (columns, left to right)
- **Ranks**: 1-8 (rows, bottom to top for white)
- **Example**: "e2" = e-file, 2nd rank (initial pawn position)

## Project Structure

```
chess_analyzer/
├── components/
│   ├── __init__.py
│   └── st_chessboard.py      # Custom chess board component
├── services/
│   ├── __init__.py
│   └── analyzer.py           # AI analysis service
├── streamlit_app.py          # Main application
├── requirements.txt          # Python dependencies
└── README.md                # Project documentation
```

## Key Components

### Chess Engine (`st_chessboard.py`)
- Complete chess rule implementation
- Move generation and validation
- Special moves (castling, en passant, promotion)
- Check and checkmate detection
- Game state management

### AI Analyzer (`analyzer.py`)
- OpenAI API integration
- Position analysis and evaluation
- Move recommendations
- Educational chess insights

### Main Application (`streamlit_app.py`)
- Streamlit interface and layout
- User interaction handling
- Game flow management
- UI components and styling

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for AI analysis features

## Dependencies

Key dependencies include:
- `streamlit`: Web application framework
- `openai`: AI analysis capabilities
- `python-dotenv`: Environment variable management

See `requirements.txt` for complete list.