
# FastAPI service exposing:
#   POST /extract   -> structured attribute JSON for a product description
#   GET  /health     -> liveness check




"""Run locally:
  uvicorn src.api:app --reload --port 8000
Example request:
  curl -X POST http://localhost:8000/extract 
       -H "Content-Type: application/json" 
       -d '{"text": "Off shoulder satin ball gown with corset bodice and sweep train in royal navy"}'
"""


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Union, Dict

from src.hybrid_extractor import extract

app = FastAPI(
    title="Product Attribute Extraction API",
    description="Converts unstructured fashion product descriptions into structured attributes.",
    version="1.0.0",
)


class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, example=(
        "Floor length chiffon bridesmaid dress with pleated bodice and "
        "V neckline available in sage and dusty blue"
    ))
    include_debug: bool = Field(
        False, description="If true, include per-attribute source (rule/ml/none) in the response."
    )


class ExtractResponse(BaseModel):
    input_text: str
    attributes: Dict[str, Union[str, List[str]]]
    debug: Dict = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/extract", response_model=ExtractResponse)
def extract_attributes(req: ExtractRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text must not be empty")

    attributes, meta = extract(text)

    response = {
        "input_text": text,
        "attributes": attributes,
    }
    if req.include_debug:
        response["debug"] = meta
    return response
