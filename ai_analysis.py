import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
prompt_text = f"""You are a longevity expert working alongside Peter Attia. Analyze this data and generate useful insights and recommendations. What patterns do you see and what is worth trying out. Here is the data: 2024-02-01: Heart Rate = 65
2024-02-02: Heart Rate = 70
2024-02-03: Heart Rate = 68
2024-02-04: Heart Rate = 72
2024-02-05: HRV = 45
2024-02-06: HRV = 50
2024-02-07: HRV = 48
2024-02-08: Sleep Duration = 7.5
2024-02-09: Sleep Duration = 6.8
2024-02-10: Sleep Duration = 7.2
2024-02-11: Glucose = 85
2024-02-12: Glucose = 90
2024-02-13: Glucose = 88
2024-02-14: Glucose = 92 """

def openai_connection(prompt_text): 
    try:
        response = openai.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {
                    "role": "developer",
                    "content": [
                        {
                            "type": "text",
                            "text": "You are Peter Attia's trusted assistant. Analyze this data and generate useful insights and recommendations. What patterns do you see and what is worth trying out"
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_text
                        }
                    ]
                }
            ],
            max_tokens=10000,
            temperature=0.7
        )
        ai_content = response.choices[0].message.content
    except Exception as e:
        return f"Error calling OpenAI: {str(e)}"
    
    return ai_content

# Example usage:
if __name__ == '__main__':
    prompt = "Can you analyze the health data in this thread and find meaningful insights?"
    analysis = openai_connection(prompt_text)
    # AI Analysis completed
