import os
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.cloud import dialogflow_v2 as dialogflow


# =====================================================
# GOOGLE CREDENTIALS (RENDER SAFE)
# =====================================================

creds_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")

if not creds_json:
    raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS_JSON not set")

# Create credentials file at runtime
with open("credentials.json", "w") as f:
    f.write(creds_json)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"


# =====================================================
# DIALOGFLOW SETUP
# =====================================================

PROJECT_ID = "hotel-booking-gneg"

session_client = dialogflow.SessionsClient()

session_id = str(uuid.uuid4())

session = session_client.session_path(
    PROJECT_ID,
    session_id
)


# =====================================================
# FASTAPI SETUP
# =====================================================

app = FastAPI()

# Allow frontend requests (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    message: str


# =====================================================
# DIALOGFLOW FUNCTION
# =====================================================

def detect_intent(text):
    text_input = dialogflow.TextInput(
        text=text,
        language_code="en"
    )

    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={
            "session": session,
            "query_input": query_input
        }
    )

    return response.query_result.fulfillment_text


# =====================================================
# API ENDPOINT
# =====================================================

@app.post("/chat")
def chat(msg: Message):
    reply = detect_intent(msg.message)
    return {"reply": reply}
