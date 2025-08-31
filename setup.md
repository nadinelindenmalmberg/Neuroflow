# Setup Guide

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database_name

# Flask Configuration
FLASK_PORT=5174
SECRET_KEY=your-secret-key-here

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174

# Oura Ring Configuration (Optional)
OURA_API_TOKEN=your-oura-api-token-here
```

## Getting API Keys

### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Create a new API key
4. Copy the key and add it to your `.env` file

### Supabase Database
1. Go to https://***REMOVED***m
2. Create a new project
3. Go to Settings > Database
4. Copy the connection string
5. Replace the placeholder in your `.env` file

### Oura Ring API Token
1. Go to https://cloud.ouraring.com/personal-access-tokens
2. Sign in to your Oura account
3. Create a new personal access token
4. Copy the token and add it to your `.env` file as `OURA_API_TOKEN`

## Quick Commands

```bash
# Install dependencies
pip install -r requirements.txt
cd my-vue-app && npm install

# Start backend (from root directory)
DATABASE_URL="your-connection-string" OPENAI_API_KEY="your-api-key" python3 app.py

# Start frontend (from my-vue-app directory)
npm run dev
```
