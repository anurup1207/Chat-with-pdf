from fastapi import FastAPI, Form, HTTPException
from typing import Dict, List
from pydantic import BaseModel
from twilio.twiml.messaging_response import MessagingResponse
from openai import AzureOpenAI
import os
from datetime import datetime
from llm import LLMClient

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

async def execute(form: Dict, message: str) -> str:
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

@app.post("/ask")
async def livrator_onboarding(
    WaId: str = Form(...), 
    AccountSid: str = Form(...),
    Body: str = Form(...)
):
  
    # Process the message
    message = Body.lower()
    form ={
        "WaId":WaId,
        "AccountSid":AccountSid
    }
    
    # Create Twilio response
    resp = MessagingResponse()
    
    # Get response from execute function
    response = await execute(form=form, message=message)
    
    # Add message to response
    reply = resp.message(response)
    
    # Return as string to match Twilio's expected format
    return str(resp)
        
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500,
    #         detail=f"Error processing request: {str(e)}"
    #     )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)