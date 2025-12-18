# Neuroflow

A comprehensive health data visualization platform with AI-powered insights, featuring a Flask REST API backend and modern Vue.js frontend. Track, analyze, and visualize health metrics from multiple sources including Oura Ring and Fitbit.

## 🚀 Features

- **Health Data Visualization**: Interactive graphs and charts for tracking health metrics over time
- **AI-Powered Analysis**: OpenAI GPT integration for intelligent health insights and recommendations
- **Device Integrations**: 
  - Oura Ring (sleep, HRV, heart rate, breathing)
  - Fitbit (steps, activity, heart rate, sleep)
- **Experiment Tracking**: Create and monitor health experiments with progress tracking
- **Modern Tech Stack**: Vue.js 3, Flask, PostgreSQL, ApexCharts
- **Real-time Sync**: Automated data synchronization from connected devices

## 📋 Prerequisites

- Python 3.8+ (Python 3.13+ recommended)
- Node.js 16+ and npm
- PostgreSQL database (Supabase recommended)
- (Optional) OpenAI API key for AI features
- (Optional) Oura API token or Fitbit OAuth credentials for device integrations

## 🛠️ Installation

### Backend Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd Neuroflow-latest
```

2. **Create a virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:

Create a `.env` file in the root directory:
```bash
# Required
DATABASE_URL=postgresql://username:password@your-database-host:port/database_name
SECRET_KEY=your-unique-secret-key-change-in-production

# Optional - Flask Configuration
FLASK_PORT=5174
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174

# Optional - OpenAI (for AI features)
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Fitbit OAuth
FITBIT_CLIENT_ID=your_fitbit_client_id_here
FITBIT_CLIENT_SECRET=your_fitbit_client_secret_here
FITBIT_REDIRECT_URI=http://localhost:5174/auth/fitbit/callback
```

5. **Run database migrations**:
```bash
flask db upgrade
```

6. **Start the Flask API server**:
```bash
python3 app.py
```

The API will be available at `http://localhost:5174`

### Frontend Setup

1. **Navigate to the frontend directory**:
```bash
cd my-vue-app
```

2. **Install dependencies**:
```bash
npm install
```

3. **Configure API URL** (optional):

Create a `.env` file in `my-vue-app/`:
```bash
VITE_API_URL=http://localhost:5174
```

4. **Start the development server**:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 📁 Project Structure

```
Neuroflow-latest/
├── app.py                      # Flask API backend server
├── models.py                   # SQLAlchemy database models
├── ai_analysis.py              # AI analysis functionality
├── requirements.txt            # Python dependencies
├── migrations/                 # Database migration files
├── utils/
│   └── services/
│       ├── oura_fetch_and_store.py      # Oura data integration
│       ├── oura_sync_manager.py         # Oura sync automation
│       ├── fitbit_oauth.py              # Fitbit OAuth handling
│       ├── fitbit_fetch_and_store.py    # Fitbit data integration
│       └── fitbit_sync_manager.py      # Fitbit sync automation
└── my-vue-app/                 # Vue.js frontend
    ├── src/
    │   ├── components/         # Vue components
    │   ├── services/          # API service layer
    │   ├── composables/       # Vue composables
    │   └── config.js          # Configuration
    └── package.json           # Node dependencies
```

## 🔌 API Endpoints

### Graphs
- `GET /api/graphs` - List all graphs
- `POST /api/graphs` - Create new graph
- `DELETE /api/graphs/<id>` - Delete graph
- `GET /api/graphs/<id>` - Get graph details

### Data Points
- `POST /api/datapoints` - Add data points
- `GET /api/datapoints` - Query data points

### AI Analysis
- `POST /api/ai-analyze/<id>` - Generate AI analysis for a graph

### Experiments
- `GET /api/experiments` - List all experiments
- `POST /api/experiments` - Create new experiment
- `GET /api/experiments/<id>` - Get experiment details
- `POST /api/experiments/<id>/complete` - Complete an experiment

### Integrations
- `GET /api/integrations/status` - Get integration status
- `POST /api/integrations/oura/sync-now` - Manually sync Oura data
- `POST /api/integrations/fitbit/sync-now` - Manually sync Fitbit data
- `GET /api/integrations/fitbit/auth-url` - Get Fitbit OAuth URL

## 🛡️ Security

This codebase follows security best practices:

- ✅ All sensitive data stored in environment variables
- ✅ No hardcoded credentials or API keys
- ✅ Proper logging without exposing sensitive information
- ✅ SQL injection protection via SQLAlchemy ORM
- ✅ CORS configuration for API security
- ✅ Input validation and error handling

**Important**: Never commit `.env` files or expose sensitive credentials. The `.gitignore` file is configured to prevent accidental commits.

## 🧪 Development

### Running in Development Mode

1. Start the backend:
```bash
source venv/bin/activate
python3 app.py
```

2. Start the frontend (in a separate terminal):
```bash
cd my-vue-app
npm run dev
```

### Database Migrations

Create a new migration:
```bash
flask db migrate -m "Description of changes"
```

Apply migrations:
```bash
flask db upgrade
```

## 🏗️ Technologies Used

- **Backend**: 
  - Flask 2.3.2
  - SQLAlchemy 3.0.3
  - PostgreSQL (via Supabase)
  - OpenAI API
  - Flask-APScheduler

- **Frontend**: 
  - Vue.js 3
  - Vite
  - ApexCharts
  - Tailwind CSS
  - Vue Router

- **Database**: 
  - PostgreSQL (Supabase)

- **DevOps**: 
  - Flask-Migrate
  - python-dotenv

## 📊 Data Sources

The application supports data from:
- **Oura Ring**: Sleep duration, HRV, heart rate, breathing rate, deep/REM sleep
- **Fitbit**: Steps, activity, heart rate, sleep data
- **Manual Entry**: Custom metrics and tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Oura Ring API
- Fitbit Web API
- OpenAI GPT
- Supabase
