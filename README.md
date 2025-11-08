# Clearwater ERLC Dashboard

A web dashboard and Discord bot for ERLC server management.

## Project Structure

- `/website/frontend` - React frontend
- `/website/backend` - Flask backend API
- `/bot.py` - Discord bot

## Environment Variables Required

### Backend
- `FLASK_SECRET_KEY` - Secret key for Flask sessions
- `ERLC_TOKEN` - Your ERLC API token
- `ERLC_SERVER_ID` - Your ERLC server ID
- `DATABASE_URL` - Database connection URL (provided by Railway)

### Frontend
- `VITE_API_URL` - Backend API URL

### Discord Bot
- `DISCORD_TOKEN` - Discord bot token