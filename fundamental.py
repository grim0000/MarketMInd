from huggingface_hub import InferenceClient

def perform_fundamental_analysis(symbol, api_key):
    client = InferenceClient(api_key=api_key)
    prompt = f"Provide a detailed fundamental analysis and put it into individual points with bold headlines for the stock symbol '{symbol}'."
    messages = [{"role": "user", "content": prompt}]
    try:
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.2-1B-Instruct",
            messages=messages,
            max_tokens=500
        )
        return completion.choices[0].message['content']
    except Exception as e:
        return f"Error generating fundamental analysis: {e}"
