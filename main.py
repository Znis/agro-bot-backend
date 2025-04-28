import uvicorn
from contextlib import asynccontextmanager
from app import create_app
from app.core import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app):
    # Connect to MongoDB on startup
    await connect_to_mongo()
    yield
    # Close MongoDB connection on shutdown
    await close_mongo_connection()

app = create_app(lifespan=lifespan)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 