{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # mcp-jotform (tiny helper)\
\
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