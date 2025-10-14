## 📦 Installation Package (Windows PowerShell)

# Requires: Python 3.11+, Node.js 18+

Write-Host "🚀 Installing Internify..." -ForegroundColor Cyan

# Backend setup
Write-Host "`n📦 Setting up backend..." -ForegroundColor Yellow
Set-Location backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env -ErrorAction SilentlyContinue
Write-Host "✅ Backend dependencies installed!" -ForegroundColor Green

# Frontend setup
Write-Host "`n📦 Setting up frontend..." -ForegroundColor Yellow
Set-Location ../frontend
npm install
Copy-Item .env.local.example .env.local -ErrorAction SilentlyContinue
Write-Host "✅ Frontend dependencies installed!" -ForegroundColor Green

Set-Location ..

Write-Host "`n✨ Installation complete!" -ForegroundColor Cyan
Write-Host @"

Next steps:
1. Edit backend/.env with your API keys
2. Edit frontend/.env.local with your Supabase credentials
3. Set up Supabase tables (see SETUP.md)
4. Run 'npm run dev' in frontend/
5. Run 'uvicorn main:app --reload' in backend/

See SETUP.md for detailed instructions.
"@ -ForegroundColor White
