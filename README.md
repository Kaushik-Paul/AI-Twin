# AI Twin Project

A personal AI assistant that can mimic your communication style and assist with tasks.

## Project Structure

- `backend/`: Python FastAPI server
  - `server.py`: Main application server
  - `requirements.txt`: Python dependencies
  - `.env`: Environment configuration

- `frontend/`: React/TypeScript web interface
  - Components and pages for the AI Twin interface

- `memory/`: Stores AI training data and memories

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env` file

4. Run the server:
   ```bash
   uvicorn server:app --reload
   ```

### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

## Usage

- Access the web interface at `http://localhost:3000`
- The AI Twin API will be available at `http://localhost:8000`

## Development

- Follow the coding standards and patterns established in the project
- Create feature branches for new work
- Submit pull requests for review

## License

[Add your license here]