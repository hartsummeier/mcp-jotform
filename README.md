## What this does\
- Talks to Jotform with YOUR API key.\
- Gives simple URLs I (your assistant) can call to read questions, submissions, and files.\
\
## How to run it locally\
1) Install Python 3.11+.\
2) In this folder, run:\
   pip install -r requirements.txt\
3) Set env vars (Mac/Linux example):\
   export JOTFORM_API_KEY=YOUR_KEY_HERE\
   export ALLOWED_FORM_IDS=123456789012345\
   export MCP_NAME=jotform\
4) Start the server:\
   python server.py\
5) Test:\
   curl http://localhost:8080/\
}
