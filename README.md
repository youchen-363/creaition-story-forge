# CreAItion 

CreAItion is an AI-powered storytelling platform that enables users to transform simple ideas into fully illustrated, narrative-rich experiences. By combining advanced language models with image generation tools, the app allows anyone—whether a writer, educator, or creative hobbyist—to upload a story outline and character details, and instantly receive a complete visual story or comic. Designed to make storytelling accessible and engaging, CreAItion is especially valuable for producing children’s books, webcomics, and even educational visuals for school textbooks. It’s where imagination meets automation to bring stories to life.

## What technologies are used for this project?

This project is built with:
- Backend: Python (FastAPI)
- Frontend: Typescript (ReactJS + Vite), TailwindCSS
- Database & Cloud Storage: Supabase
- AI Integration: mllm gemini-2.5-flash & gemini-2.0-flash-preview-image-generation


## Project Structure

```
project-root/
├── backend/               ← Python FastAPI backend
│   ├── .env               ← Backend secrets (Gemini & Supabase API key)
│   ├── requirements.txt   ← Python dependencies
│   ├── fast_api.py        ← Main FastAPI application
│   ├── dao.py             ← Database access layer
│   └── ...                ← Other backend modules
├── frontend/              ← React/TypeScript frontend
│   ├── .env               ← Frontend config (Supabase API key)
│   ├── package.json       ← Node.js dependencies
│   ├── src/               ← React components and hooks
│   └── ...                ← Other frontend files
├── database_setup.sql     ← PostgreSQL schema for Supabase
└── README.md              
```

## Quick Start

### Development (Local)

1. **Clone the repository**
   ```bash
   git clone https://github.com/youchen-363/creaition-story-forge.git
   cd creaition-story-forge
   ```

2. **Setup Backend**
   ```bash
   cd backend
   
   # Create virtual environment (recommended)
   python -m venv venv
   
   venv\Scripts\activate  # On Windows PowerShell
   source venv/bin/activate # Linux / Mac 
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run backend
   python fast_api.py
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   
   # Install dependencies
   npm install
   
   # Run frontend
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8002
   - API Docs: http://localhost:8002/docs

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
cd frontend

# Install dependencies
npm i

# Start the development server with auto-reloading and an instant preview.
npm run dev
```

## Environment Variables

To run the project locally, you need to configure environment variables for both the **backend** and **frontend**.

### Backend Environment (`backend/.env`)

Create a `.env` file in the `backend/` directory with the following content:

```env
# Gemini API Keys
GEMINI_API_KEY=
GEMINI_PAID_API_KEY=

# Supabase Configuration
SUPABASE_URL=
SUPABASE_ANON_KEY=

# API Configuration
API_HOST=0.0.0.0
API_PORT=8002
```
Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey), and Supabase keys from your project settings dashboard.

---

### Frontend Environment (`frontend/.env`)

Create a `.env` file in the `frontend/` directory with the following content:

```env
# Supabase Configuration
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=

# API Configuration
VITE_API_URL=http://localhost:8002
```

