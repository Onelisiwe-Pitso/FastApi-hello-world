import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI(title="Tech TTT Speakers & Talks API")


def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")


@app.on_event("startup")
def startup_db_setup():
    conn = get_db_connection()
    cur = conn.cursor()
    # Create the Speakers table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS speakers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            company VARCHAR(100)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS talks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            speaker_id INTEGER REFERENCES speakers(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    cur.close()
    conn.close()



@app.get("/")
def read_root():
    return {"message": "Welcome to the Tech TTT Speakers and Talks API", "status": "Connected"}



@app.get("/speakers")
def get_speakers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM speakers;")
    speakers = cur.fetchall()
    cur.close()
    conn.close()
    return speakers

@app.post("/speakers")
def create_speaker(title: str, company: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO speakers (name, company) VALUES (%s, %s) RETURNING *;",
        (title, company)
    )
    new_speaker = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return new_speaker

# --- TALKS ENDPOINTS ---

@app.get("/talks")
def get_talks():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT talks.id, talks.title, speakers.name AS speaker_name 
        FROM talks 
        LEFT JOIN speakers ON talks.speaker_id = speakers.id;
    """)
    talks = cur.fetchall()
    cur.close()
    conn.close()
    return talks

@app.post("/talks")
def create_talk(title: str, speaker_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO talks (title, speaker_id) VALUES (%s, %s) RETURNING *;",
        (title, speaker_id)
    )
    new_talk = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return new_talk