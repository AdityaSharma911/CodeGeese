#!/bin/bash

ENV_NAME="codegeese-env"
REQUIREMENTS="requirements.txt"
APP_ENTRY="../src.main:app"

echo -e "\n🧠 [CodeGeese] Starting Dev Environment..."

# Step 1: Create venv if not exists
if [ ! -d "$ENV_NAME" ]; then
  echo -e "📦 Creating virtual environment: \033[1m$ENV_NAME\033[0m"
  python3 -m venv "$ENV_NAME"
fi

# Step 2: Activate venv
echo -e "🔌 Activating virtual environment: \033[1m$ENV_NAME\033[0m"
source "$ENV_NAME/bin/activate"

# Step 3: Install dependencies
if [ -f "$REQUIREMENTS" ]; then
  echo -e "📚 Installing dependencies from: \033[1m$REQUIREMENTS\033[0m"
  pip install -r "$REQUIREMENTS"
else
  echo -e "❌ \033[1m$REQUIREMENTS\033[0m not found!"
  exit 1
fi

# Step 4: Start server
echo -e "\n🚀 Launching FastAPI server..."
echo -e "🔁 Watching for changes in: \033[1msrc/\033[0m\n"

uvicorn "$APP_ENTRY" --reload --reload-dir src

