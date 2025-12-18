# How To Run TradingAgent Plus

Follow these steps to set up and run the upgraded TradingAgents environment.

## 1. Create a Virtual Environment
Create a clean python environment to manage dependencies.

```bash
python -m venv tradingagents-venv
# Windows:
.\tradingagents-venv\Scripts\activate
# Linux/Mac:
source tradingagents-venv/bin/activate
```

## 2. Install Dependencies
Install the required python packages for the backend.

```bash
pip install -r requirements.txt
```

## 3. Run the Backend Server
Start the FastAPI backend server using uvicorn.

```bash
python -m uvicorn backend.main:app --reload --port 8000
```
*The backend API will be available at http://localhost:8000/api*

## 4. Setup Frontend
Open a new terminal window and navigate to the frontend directory.

```bash
cd frontend
```

## 5. Install Frontend Dependencies
Install the Node.js packages required for the Vue.js interface.

```bash
npm install
```

## 6. Run the Frontend Development Server
Start the frontend interface.

```bash
npm run dev
```
*Access the GUI at the URL shown in the terminal (usually http://localhost:5173/)*
