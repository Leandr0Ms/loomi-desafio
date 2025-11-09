import os
import random
from dotenv import load_dotenv

from sqlalchemy import create_engine, MetaData, Table, select, func
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from fastapi import FastAPI, HTTPException

# Carrega variáveis do .env
load_dotenv()

# Lê variáveis individuais
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

# Monta a DATABASE_URL no padrão do psycopg2/SQLAlchemy
DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

app = FastAPI()

# Dicionário de respostas fixas
responses = {
    1: "You have it!",
    2: "You don't have it, I'm sorry...",
    3: "You have a lot of it! Congratulations!",
}

# Endpoint to return a random string from a dict
@app.get("/do-you-have-it")
async def do_you_have_it():
    random_number = random.randint(1, 3)
    response = responses.get(random_number, "Something went wrong...")

    return {"message": response}


# Endpoint to search for a string in the database and return an appropriate message
@app.get("/do-you-have-it-db")
async def do_you_have_it_db():
    # Setup PostgreSQL connection if DATABASE_URL is provided
    if DATABASE_URL:
        try:
            engine = create_engine(DATABASE_URL)
            metadata = MetaData()
            strings_table = Table("strings", metadata, autoload_with=engine)
            with engine.connect() as conn:
                # Select a random string from the database
                stmt = select(strings_table.c.content).order_by(func.random()).limit(1)
                result = conn.execute(stmt).fetchone()

                if result:
                    return {"message": result[0]}
                else:
                    return {"message": "No data found in the database."}

        except (SQLAlchemyError, OperationalError) as sqle:
            raise HTTPException(status_code=500, detail=f"Database error: {str(sqle)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="DATABASE_URL not found")