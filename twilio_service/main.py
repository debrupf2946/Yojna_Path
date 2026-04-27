import json
import logging
import traceback
import os
import time
from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from twilio.twiml.voice_response import VoiceResponse, Connect
from elevenlabs import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from agent import TwilioAudioInterface


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
_start_time = time.time()

eleven_labs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
ELEVEN_LABS_AGENT_ID = os.getenv("AGENT_ID")


@app.get("/")
async def root():
    return {"message": "Twilio-ElevenLabs Integration Server"}


@app.get("/health")
async def health_check():
    """Return service health status and uptime in seconds."""
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - _start_time, 2),
        "agent_id_configured": bool(ELEVEN_LABS_AGENT_ID),
    }


@app.api_route("/incoming-call-eleven", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    """Handle incoming call and return TwiML response."""
    response = VoiceResponse()
    host = request.url.hostname
    connect = Connect()
    connect.stream(url=f"wss://{host}/media-stream-eleven")
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")


@app.websocket("/media-stream-eleven")
async def handle_media_stream(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")

    audio_interface = TwilioAudioInterface(websocket)
    conversation = None

    try:
        conversation = Conversation(
            client=eleven_labs_client,
            agent_id=ELEVEN_LABS_AGENT_ID,
            requires_auth=False,
            audio_interface=audio_interface,
            callback_agent_response=lambda text: logger.info("Agent said: %s", text),
            callback_user_transcript=lambda text: logger.info("User said: %s", text),
        )

        conversation.start_session()
        logger.info("Conversation session started")

        async for message in websocket.iter_text():
            if not message:
                continue

            try:
                data = json.loads(message)
                await audio_interface.handle_twilio_message(data)
            except Exception as e:
                logger.error("Error processing message: %s", str(e))
                traceback.print_exc()

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    finally:
        if conversation:
            logger.info("Ending conversation session...")
            conversation.end_session()
            conversation.wait_for_session_end()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
