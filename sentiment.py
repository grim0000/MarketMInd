from huggingface_hub import InferenceClient

def perform_sentiment_analysis(symbol):
    # Replace 'your_api_key_here' with your actual Hugging Face API key
    api_key = "Your_api_key"
    client = InferenceClient(api_key=api_key)
    
    # Prepare the prompt for sentiment analysis
    prompt = f"Provide a sentiment analysis for the stock symbol '{symbol}' search and include recent headlines and sentiments ."
    messages = [{"role": "user", "content": prompt}]
    
    try:
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.2-1B-Instruct",
            messages=messages,
            max_tokens=200  # Adjust token limit as needed
        )
        response = completion.choices[0].message['content']
        
        # Parse the returned response into sentiment and headlines
        sentiment_data = {
            "symbol": symbol,
            "sentiment": response.split("\n")[0].strip(),
            "headlines": [line.strip() for line in response.split("\n")[1:] if line.strip()]
        }
        return sentiment_data
    
    except Exception as e:
        return {"error": f"Error performing sentiment analysis: {e}"}
