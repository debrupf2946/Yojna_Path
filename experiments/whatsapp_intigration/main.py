from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from twilio.twiml.messaging_response import MessagingResponse
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)
from API_KEYS import GROQ_APIKEY
from prompts import SYSTEM_PROMPT
from groq import Groq




app=FastAPI()

gclient = Groq(api_key=GROQ_APIKEY)


messages_history = [{"role": "system", "content": SYSTEM_PROMPT}]


def generate_answer(question: str):
    

    
    messages_history.append({"role": "user", "content": question})
    
    completion = gclient.chat.completions.create(
                    model="mixtral-8x7b-32768",
                    messages=messages_history,
                    temperature=0.5,
                    max_tokens=200,
                    top_p=1,
                    stream=False,
                )
                
    assistant_response = completion.choices[0].message.content
    print("Response from Groq client:", assistant_response)
    messages_history.append({"role": "assistant", "content": assistant_response})
    
    return assistant_response

@app.get("/")
def root():
    return {"message": "hello world"}


@app.api_route("/grock",methods=["POST"])
async def grock(request: Request):
    form_data = await request.form()  
    incoming_question = form_data.get("Body", "").lower()
    
    genearated_answer=generate_answer(incoming_question)
    
    return genearated_answer



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)