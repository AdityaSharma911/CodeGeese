pip install -r requirements.txt
#create env
python3 -m venv codegeese-env
#change env
source codegeese-env/bin/activate
# Start server
uvicorn src.main:app --reload --reload-dir src