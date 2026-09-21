import asyncio
import logging
import os
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Use absolute path to ensure we find the right .env
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))
load_dotenv(".env") # also try local

from core.llm_factory import LLMFactory
from core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_fallback():
    print("\n--- Testing LLM Fallback (Gemini 429 -> Groq) ---\n")
    
    # 1. Create a simple chain
    prompt = ChatPromptTemplate.from_template("Tell me a short joke about {topic}")
    llm = LLMFactory.get_llm(temperature=0.7)
    chain = prompt | llm | StrOutputParser()
    
    # 2. Mock ChatGoogleGenerativeAI to raise a 429 error
    # We need to find where ChatGoogleGenerativeAI is instantiated or used.
    # Since with_fallbacks is used, the chain.ainvoke will first try the primary LLM.
    
    with patch("langchain_google_genai.chat_models.ChatGoogleGenerativeAI.ainvoke") as mock_gemini:
        # Create a mock exception that looks like a 429
        mock_gemini.side_effect = Exception("429 RESOURCE_EXHAUSTED: You exceeded your current quota")
        
        print("Simulating Gemini 429 error...")
        
        try:
            # This should trigger the fallback to Groq
            # Note: Since we mocked ainvoke on the class or instance, 
            # with_fallbacks should catch it if it's the first in the list.
            result = await LLMFactory.invoke_with_fallback(chain, {"topic": "bears"})
            print(f"\n✅ Fallback Successful! Response from Fallback LLM:\n{result}")
        except Exception as e:
            print(f"\n❌ Fallback Failed: {str(e)}")
            raise e

if __name__ == "__main__":
    asyncio.run(test_fallback())
