from google import genai
from database import getUserData
import json
from datetime import datetime

# Initialize Gemini AI Client
client = genai.Client(api_key='AIzaSyDQSaDT6K3IoKeW70-g8uPNSCISi51KSnE')


async def askAItoAnswer(tgID, userMessage):
    """Communicates with Gemini AI to parse user intent and return structured JSON."""
    data = getUserData(tgID)
    time_now = datetime.now().strftime("%d.%m.%Y, %A")

    # System instructions for the AI to ensure consistent JSON output
    base_rules = f"""
            RULES:
            1. Today is {time_now}. Use this as your reference.
            2. DATA RULE: If Name, Phone, or City exists in the "CONTEXT", fill the "data" block. 
               Do not leave them null if information is available!
            3. LOGIC: If user mentions a day (e.g., "Saturday"), calculate the date based on {time_now}.
            4. IS_COMPLETE: Set to true only if ALL fields (name, phone, city, date) are filled.
            5. NORMALIZATION: All city names MUST be in the nominative case (називний відмінок).
               Example: "у Києві" -> "Київ", "в Обухові" -> "Обухів", "у Чабанах" -> "Чабани".

            JSON STRUCTURE:
            {{
                "reply": "Your polite response or a question about missing info",
                "is_complete": true/false,
                "data": {{ "name": "name/null", "phone": "number/null", "date": "DD.MM.YYYY/null", "city": "city/null" }}
            }}
        """

    context = f"DB Data: Name: {data.get('name')}, Tel: {data.get('phone')}, City: {data.get('city')}" if data else "New client, no history."

    prompt = f"""
        Role: Epiland Administrator. Goal: Fill the JSON structure based on conversation.
        CONTEXT: {context}
        USER MESSAGE: "{userMessage}"
        {base_rules}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',  # Updated to a stable flash model
            contents=prompt
        )

        if not response.text:
            raise ValueError("Empty response from AI")

        # Clean Markdown formatting from AI response to get pure JSON
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)

    except Exception as e:
        print(f"AI/JSON Error: {e}")
        return {
            "reply": "I'm experiencing some technical difficulties. Please try again later!",
            "is_complete": False,
            "data": {"name": None, "phone": None, "date": None, "city": None}
        }