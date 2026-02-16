import os
import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from google.cloud import dialogflow_v2 as dialogflow


# -------------------------------
# Dialogflow Setup
# -------------------------------

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "hotel-booking-gneg-252a22ec945f.json"

PROJECT_ID = "hotel-booking-gneg"

session_client = dialogflow.SessionsClient()

session_id = str(uuid.uuid4())

session = session_client.session_path(
    PROJECT_ID,
    session_id
)


# -------------------------------
# FastAPI App
# -------------------------------

app = FastAPI()


class Message(BaseModel):
    message: str


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


@app.post("/chat")
def chat(msg: Message):
    reply = detect_intent(msg.message)
    return {"reply": reply}
