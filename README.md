# Neuroflow

A health data visualization platform with AI-powered insights, featuring a Flask API backend and Vue.js frontend.

## Features

- Health data visualization and tracking
- AI-powered analysis and recommendations
- Oura Ring integration
- Interactive graphs and charts
- Modern Vue.js frontend
- Supabase PostgreSQL database

## Project Structure

- `app.py` - Flask API backend server
- `my-vue-app/` - Vue.js frontend application
- `models.py` - Database models
- `ai_analysis.py` - AI analysis functionality
- `utils/services/oura_fetch_and_store.py` - Oura data integration

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend (Flask API)

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Set up environment variables:

Create a `.env` file in the root directory:
```bash
DATABASE_URL=postgresql://***REMOVED***:***REMOVED***@***REMOVED***:6543/postgres
FLASK_PORT=5174
OPENAI_API_KEY=your_openai_api_key_here
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174
```

3. Run the Flask API server:

```bash
DATABASE_URL="postgresql://***REMOVED***:***REMOVED***@***REMOVED***:6543/postgres" FLASK_PORT=5174 python3 app.py
```

The API will be available at `http://localhost:5174`

### Frontend (Vue.js)

1. Navigate to the frontend directory:

```bash
cd my-vue-app
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Development

- **Backend API**: `http://localhost:5174`
- **Frontend**: `http://localhost:5173`
- **Database**: Supabase PostgreSQL
- **API Endpoints**: `/api/*`

The frontend automatically proxies API requests to the backend.

## API Endpoints

- `GET /api/graphs` - List all graphs
- `POST /api/graphs` - Create new graph
- `DELETE /api/graphs/<id>` - Delete graph
- `POST /api/datapoints` - Add data points
- `POST /api/ai-analyze/<id>` - AI analysis
- `POST /api/oura-connect` - Oura data import

## Technologies Used

- **Backend**: Flask, SQLAlchemy, OpenAI API, PostgreSQL
- **Frontend**: Vue.js 3, Vite, Tailwind CSS, ApexCharts
- **Database**: Supabase PostgreSQL
- **AI**: OpenAI GPT for health insights
- **Data Integration**: Oura Ring API

## Data Sources

The application currently includes:
- Oura Ring sleep and health data
- Strength training metrics
- Sleep analysis (Deep & REM sleep tracking)
