"""ExchangeServer — FastAPI server for USDx wallets and x402 contracts."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

app = FastAPI(title="ExchangeServer", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# In-memory stores
wallets: dict = {}
contracts: dict = {}
messages: dict = {}

def init_wallet(parcel_id: str) -> dict:
    return {
        "parcel_id": parcel_id,
        "address": f"0x{parcel_id.replace('-','')[:40].ljust(40,'0')}",
        "asset_symbol": "USDx",
        "protocol": "x402",
        "balance": 200.0,
        "monthly_limit": 500.0,
        "spent_this_month": 0.0,
        "chain_id": 80001,
        "chain_name": "polygon-mumbai-testnet"
    }

@app.get("/wallet/{parcel_id}")
def get_wallet(parcel_id: str):
    if parcel_id not in wallets:
        wallets[parcel_id] = init_wallet(parcel_id)
    return wallets[parcel_id]

class ContractProposal(BaseModel):
    parcel_id: str
    counterparty_agent_id: str
    purpose: str
    asset_symbol: str = "USDx"
    rate_per_event: float
    max_total: float

@app.post("/contract/propose")
def propose_contract(req: ContractProposal):
    contract_id = str(uuid.uuid4())
    contract = {
        "contract_id": contract_id,
        "protocol": "x402",
        "parcel_id": req.parcel_id,
        "counterparty_agent_id": req.counterparty_agent_id,
        "purpose": req.purpose,
        "asset_symbol": req.asset_symbol,
        "rate_per_event": req.rate_per_event,
        "max_total": req.max_total,
        "spent_amount": 0.0,
        "remaining_amount": req.max_total,
        "status": "proposed",
        "created_at": datetime.utcnow().isoformat(),
        "signed_at": None,
        "signature": None
    }
    contracts[contract_id] = contract
    return contract

class SignRequest(BaseModel):
    parcel_id: str

@app.post("/contract/{contract_id}/sign")
def sign_contract(contract_id: str, req: SignRequest):
    if contract_id not in contracts:
        raise HTTPException(404, f"Contract {contract_id} not found")
    c = contracts[contract_id]
    if c["parcel_id"] != req.parcel_id:
        raise HTTPException(403, "Parcel ID mismatch")
    c["status"] = "signed"
    c["signed_at"] = datetime.utcnow().isoformat()
    c["signature"] = f"0xeip712sig_{contract_id[:8]}"
    return c

@app.get("/contract/{contract_id}")
def get_contract(contract_id: str):
    if contract_id not in contracts:
        raise HTTPException(404, f"Contract {contract_id} not found")
    return contracts[contract_id]

@app.get("/contracts")
def list_contracts(parcel_id: Optional[str] = None):
    all_c = list(contracts.values())
    if parcel_id:
        all_c = [c for c in all_c if c["parcel_id"] == parcel_id]
    return {"contracts": all_c, "count": len(all_c)}

class AgentMessage(BaseModel):
    from_agent_id: str
    to_agent_id: str
    topic: str
    payload: dict

@app.post("/message/send")
def send_message(msg: AgentMessage):
    msg_id = str(uuid.uuid4())
    record = {
        "message_id": msg_id,
        "protocol": "x402",
        **msg.dict(),
        "sent_at": datetime.utcnow().isoformat()
    }
    messages[msg_id] = record
    return record

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3003)
