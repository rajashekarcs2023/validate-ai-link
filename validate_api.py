from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from validate_link import validate_link

app = FastAPI()

# Allow frontend to call this from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


class LinkRequest(BaseModel):
    link: str


class LinkResponse(BaseModel):
    valid: bool
    message: str


@app.post("/validate", response_model=LinkResponse)
def validate(req: LinkRequest):
    valid, message = validate_link(req.link)
    return LinkResponse(valid=valid, message=message)
