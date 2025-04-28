from fastapi import FastAPI
from app.api import basic_router
from app.sequences import farm_ops_router

def create_app(lifespan=None):
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="AGRO: CNC Farming System API",
        lifespan=lifespan
    )
    
    # Register routers
    app.include_router(basic_router)
    app.include_router(farm_ops_router)
    
    return app 