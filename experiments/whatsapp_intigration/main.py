from fastapi import FastAPI, Request,Response
from twilio.twiml.messaging_response import MessagingResponse
import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from API_KEYS import GROQ_APIKEY
from prompts import SYSTEM_PROMPT
from groq import Groq


app = FastAPI()

gclient = Groq(api_key=GROQ_APIKEY)

messages_history = [{"role": "system", "content": SYSTEM_PROMPT}]

MAX_HISTORY = 20


async def generate_answer(question: str) -> str:
    messages_history.append({"role": "user", "content": question})

    # Keep history bounded: system prompt + last MAX_HISTORY user/assistant turns
    if len(messages_history) > MAX_HISTORY + 1:
        del messages_history[1 : len(messages_history) - MAX_HISTORY]

    try:
        completion = gclient.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=messages_history,
            temperature=0.5,
            max_tokens=200,
            top_p=1,
            stream=False,
        )
        assistant_response = completion.choices[0].message.content
    except Exception as e:
        logger.error("Groq API error: %s", e)
        messages_history.pop()
        return "Sorry, I encountered an error. Please try again."

    logger.info("Response from Groq client: %s", assistant_response)
    messages_history.append({"role": "assistant", "content": assistant_response})
    return assistant_response


@app.get("/")
def root():
    return {"message": "hello world"}


@app.api_route("/grock", methods=["POST"])
async def grock(request: Request):
    logger.info("Incoming Twilio request: %s", await request.body())
    form_data = await request.form()
    incoming_question = form_data.get("Body", "").lower()
    
    generated_answer = await generate_answer(incoming_question)
    
    logger.info("BOT Answer: %s", generated_answer)
    
    bot_resp = MessagingResponse()
    msg = bot_resp.message()
    msg.body(generated_answer)
    
    xml_response = str(bot_resp)
    return Response(content=xml_response, media_type="text/xml")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)