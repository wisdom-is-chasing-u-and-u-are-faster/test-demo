from pydantic import BaseModel


class TransactionPayload(BaseModel):
    entity_name: str
    amount: float
    currency: str = "USD"


class TransactionRequest(BaseModel):
    transaction_id: str
    tenant_id: str
    action: str = "INITIATE"
    payload: TransactionPayload


class TransactionResponse(BaseModel):
    status: str = "ACCEPTED"
    tracking_id: str
    created_at: str
    next_step: str = "AWAITING_VERIFICATION"
