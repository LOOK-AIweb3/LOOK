from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn

# Import AI Models
from models.price_prediction import PricePredictionModel
from models.risk_assessment import RiskAssessmentModel
from models.behavioral_analysis import BehavioralAnalysisModel

# Import Blockchain Interfaces
from blockchain.solana import SolanaClient
from blockchain.ethereum import EthereumClient
from blockchain.cosmos import CosmosClient

app = FastAPI(
    title="LOOK.AI API",
    description="Cross-Chain Real-time Intelligent Data Analysis Platform API",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class TokenAnalysisRequest(BaseModel):
    token_address: str
    chain_type: str
    analysis_type: List[str]

class TokenAnalysisResponse(BaseModel):
    token_metadata: dict
    market_performance: dict
    risk_assessment: dict
    recommendations: List[str]
    timestamp: datetime

# API Routes
@app.get("/")
async def read_root():
    return {"status": "ok", "message": "LOOK.AI API Service is running"}

@app.post("/api/v1/analyze", response_model=TokenAnalysisResponse)
async def analyze_token(request: TokenAnalysisRequest):
    try:
        # Initialize Blockchain Client
        clients = {
            "solana": SolanaClient(),
            "ethereum": EthereumClient(),
            "cosmos": CosmosClient()
        }
        
        # Get On-chain Data
        client = clients.get(request.chain_type)
        if not client:
            raise HTTPException(status_code=400, message="Unsupported blockchain type")
            
        token_data = await client.get_token_data(request.token_address)
        
        # AI Model Analysis
        price_model = PricePredictionModel()
        risk_model = RiskAssessmentModel()
        behavior_model = BehavioralAnalysisModel()
        
        analysis_results = {
            "token_metadata": token_data.metadata,
            "market_performance": await price_model.predict(token_data),
            "risk_assessment": await risk_model.evaluate(token_data),
            "recommendations": await behavior_model.analyze(token_data),
            "timestamp": datetime.now()
        }
        
        return TokenAnalysisResponse(**analysis_results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/chains")
async def get_supported_chains():
    return {
        "chains": [
            {"id": "solana", "name": "Solana", "status": "active"},
            {"id": "ethereum", "name": "Ethereum", "status": "active"},
            {"id": "cosmos", "name": "Cosmos", "status": "active"},
            {"id": "polkadot", "name": "Polkadot", "status": "coming_soon"}
        ]
    }

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)