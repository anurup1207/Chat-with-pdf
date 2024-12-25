from fastapi import FastAPI, Form, HTTPException, Request
from typing import Dict, List
from pydantic import BaseModel
from openai import AzureOpenAI
import os
from datetime import datetime
from llm import LLMClient
import requests
from dotenv import load_dotenv
import os

load_dotenv()


app = FastAPI()



# In-memory chat history storage
chat_histories: Dict[str, List[Dict[str,str]]] = {}

def get_chat_history(user_id: str) -> List[Dict]:
    """Retrieve chat history for a user"""
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    return chat_histories[user_id]

def save_message(user_id: str, role: str, content: str):
    """Save a message to chat history"""
    history = get_chat_history(user_id)
    history.append({
        "role": role,
        "content": content,
    })

async def execute(form: str, message: str) -> str:
    """
    Process the onboarding message using Azure OpenAI and maintain chat history
    
    Args:
        form (Dict): The complete form data
        message (str): The message body from the request
        
    Returns:
        str: Response message
    """
    # Get user identifier from the From field
    user_id = str(form['WaId'])
    
    # Get chat history
    chat_history = get_chat_history(user_id)
    
    llm_client = LLMClient()
    # Get response from Azure OpenAI
    response = await llm_client.get_response(user_question=message, conversation_history = chat_history)

    # Save user message to chat history
    save_message(user_id, "user", message)
    # Save assistant response to chat history
    save_message(user_id, "assistant", response)
    
    return response

def send_message(chat_id: int, text: str):
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.post("/ask")
async def livrator_onboarding(request: Request):
  
    # Process the message
    data = await request.json()  # Parse incoming JSON from Telegram
    chat_id = data['message']['chat']['id']
    user_message = data['message']['text']
    message = user_message.lower()
    
    # Get response from execute function
    response = await execute(form=chat_id, message=message)
    
    send_message(chat_id, response)
    return {"status": "ok"}
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500,
    #         detail=f"Error processing request: {str(e)}"
    #     )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
