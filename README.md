Scalable LLM Chatbot System Documentation:-

Overview:--

This project is a scalable chat application powered by a Large Language Model (LLM) designed to handle over 10,000 users. The system supports user authentication, conversation history management, and context-aware responses while ensuring efficiency, scalability, and reliability.
Documentation Drive Link:

Installation & Setup:-

Prerequisites

Ensure you have the following installed:

1)Python 3.9+
2)PostgreSQL (NeonDB)
3)Streamlit
4)FastAPI
5)Prisma

1. Clone the Repository

git clone https://github.com/Bhuvanagajjarapu/SERVAM.AI

cd python_chatboat

2. Install Dependencies

pip install -r requirements.txt

3. Set Up Database

Create a NeonDB PostgreSQL instance,
Set up environment variables in .env,
DATABASE_URL=postgresql://your_neondb_url

Run:-prisma migrate dev

4. Start Backend (FastAPI)

uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

5. Start Frontend (Streamlit)

streamlit run frontend/app.py

Future Improvements:-

WebSockets + FastAPI for real-time chat streaming
Redis for efficient session caching

