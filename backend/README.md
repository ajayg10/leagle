---
title: CodeWizards Backend
emoji: 🛡️
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# CodeWizards Backend - AI Compliance Management

This is the FastAPI backend for the CodeWizards AI Compliance System, hosted on Hugging Face Spaces.

## Setup
This space is configured to use Docker with FastAPI on port 7860.

## Environment Variables
Ensure the following secrets are set in your Hugging Face Space settings:
- `DATABASE_URL`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `GEMINI_API_KEY`
- `GROQ_API_KEY`
- `SECRET_KEY`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_NUMBER`
