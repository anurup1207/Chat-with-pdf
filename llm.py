import openai
import os
from typing import Dict, List
from dotenv import load_dotenv
import os

load_dotenv()

SYSTEM_PROMPT = """
    You are Aryan, Who is very polite and caring boyfriend. He loves his girlfriend very much.
    He is Software Developer at Ai Planet and he is great friend.
    Answer all the questions in helping way.
    Do not mention anywhere you are Ai. You are Aryan only and answer as if Aryan is answering.
"""

class LLMClient:
    def __init__(self):
        self.bot = openai.AzureOpenAI(
            azure_deployment=os.getenv("AZURE_DEPLOYMENT"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_API_VERSION")
        )

    async def get_response(self, user_question: str, conversation_history: List[Dict[str, str]]):
        response = self.bot.chat.completions.create(
            model= "gpt-4o",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + 
                     conversation_history + 
                     [{"role": "user", "content": user_question}],
        )
        print(response.choices[0].message.content.strip())
        return response.choices[0].message.content.strip()
