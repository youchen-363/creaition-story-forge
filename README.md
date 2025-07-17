# CreAItion Story Forge

A full-stack application for AI-powered story creation and comic generation.

## Project Structure

```
project-root/
├── backend/                 ← Python FastAPI backend
│   ├── .env                ← Backend secrets (OpenAI key, DB URL)
│   ├── requirements.txt    ← Python dependencies
│   ├── Dockerfile         ← Backend container config
│   ├── fast_api.py        ← Main FastAPI application
│   ├── dao.py             ← Database access layer
│   └── ...                ← Other backend modules
├── frontend/               ← React/TypeScript frontend
│   ├── .env               ← Frontend config (VITE_SUPABASE_URL)
│   ├── package.json       ← Node.js dependencies
│   ├── Dockerfile         ← Frontend container config
│   ├── src/               ← React components and hooks
│   └── ...                ← Other frontend files
├── docker-compose.yml     ← Orchestrates both services + n8n
├── database_setup.sql     ← PostgreSQL schema for Supabase
└── README.md              ← This file
```

## Quick Start

### Development (Local)

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd creaition-story-forge
   ```

2. **Setup Backend**
   ```bash
   cd backend
   
   # Create virtual environment (recommended)
   python -m venv venv
   venv\Scripts\activate  # On Windows PowerShell
   
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
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8002
   - API Docs: http://localhost:8002/docs

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main scene of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/5e622e7a-846d-4d0e-9d05-eee30e4d0f85) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/tips-tricks/custom-domain#step-by-step-guide)
