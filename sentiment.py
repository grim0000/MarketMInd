from groq import Groq
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def perform_sentiment_analysis(symbol):
    # Initialize Groq client
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"error": "Groq API key not found in .env file"}
    
    client = Groq(api_key=api_key)
    
    # Prepare the prompt for sentiment analysis
    prompt = (
        f"Perform a sentiment analysis for the stock symbol '{symbol}'. "
        f"Provide an overall sentiment (Positive, Negative, or Neutral) and list 3 recent hypothetical headlines related to the stock with their individual sentiments. "
        f"Format the response as follows:\n"
        f"Overall Sentiment: [Positive/Negative/Neutral]\n"
        f"Headlines:\n"
        f"1. [Headline 1] - [Sentiment]\n"
        f"2. [Headline 2] - [Sentiment]\n"
        f"3. [Headline 3] - [Sentiment]"
    )
    
    try:
        # Call Groq's chat completion API
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
        
        # Extract the response
        response = completion.choices[0].message.content.strip()
        
        # Parse the response
        sentiment_match = re.search(r"Overall Sentiment: (Positive|Negative|Neutral)", response)
        overall_sentiment = sentiment_match.group(1) if sentiment_match else "Neutral"
        
        headlines = []
        headline_matches = re.findall(r"\d+\.\s*(.*?)\s*-\s*(Positive|Negative|Neutral)", response)
        for headline, sentiment in headline_matches:
            headlines.append(f"{headline} - {sentiment}")
        
        # Fallback for missing headlines
        while len(headlines) < 3:
            headlines.append(f"No recent news available for {symbol} - Neutral")
        
        # Return structured data
        sentiment_data = {
            "symbol": symbol,
            "sentiment": overall_sentiment,
            "headlines": headlines
        }
        return sentiment_data
    
    except Exception as e:
        return {"error": f"Error performing sentiment analysis: {e}"}