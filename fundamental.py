from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def perform_fundamental_analysis(symbol):
    # Initialize Groq client
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Error: Groq API key not found in .env file"
    
    client = Groq(api_key=api_key)
    
    # Prepare the prompt for fundamental analysis
    prompt = (
        f"Provide a detailed fundamental analysis for the stock symbol '{symbol}'. "
        f"Format the response as a bulleted list with bold headlines for each point (e.g., **Revenue Growth**, **Profit Margins**). "
        f"Cover aspects like financial performance, market position, growth prospects, and risks."
    )
    
    try:
        # Call Groq's chat completion API
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        
        # Return the response
        return completion.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Error generating fundamental analysis: {e}"