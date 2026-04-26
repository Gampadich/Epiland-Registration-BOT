import os
from dotenv import load_dotenv
from google import genai
from Database import getUserData
import json
from datetime import datetime
from CalculateData import get_calculated_date
from ValidateNumber import validateNumber

# Initialize Gemini AI Client

load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_TOKEN'))


async def askAItoAnswer(tgID, userMessage, history=''):
    """Communicates with Gemini AI to parse user intent and return structured JSON."""
    data = getUserData(tgID)
    today = datetime.now()

    # System instructions for the AI to ensure consistent JSON output
    base_rules = f"""
                RULES:
                1. DATA RULE: Use "CONTEXT" to fill the "data" block. Do not leave null if info is available!
                2. DATE LOGIC (CRITICAL): Do not calculate DD.MM.YYYY. 
                   Instead, fill "date_params" object:
                   - "day": English weekday name (monday, tuesday, wednesday, thursday, friday, saturday, sunday) or null.
                   - "weeks_added": 0 for this week, 1 for "next week", etc.
                   - "is_today": true if user says "today" or "now".
                   - "is_tomorrow": true if user says "tomorrow".
                   - "exact_date": If user provides a specific date like "25.04", put it here.
                3. IS_COMPLETE: true only if name, phone, city are filled AND any date info is present in date_params.
                4. NORMALIZATION: City names MUST be in nominative case (Київ, Обухів).
                5. LANGUAGE RULE: Use correct Ukrainian grammar and declension (відмінювання). The name "Epiland" in the instrumental case is "Епіландом".

                JSON STRUCTURE:
                {{
                    "reply": "text",
                    "is_complete": true/false,
                    "data": {{ 
                        "name": "name/null", 
                        "phone": "number/null", 
                        "city": "city/null",
                        "date_params": {{
                            "day": "string/null",
                            "weeks_added": 0,
                            "is_today": false,
                            "is_tomorrow": false,
                            "exact_date": "string/null"
                        }}
                    }}
                }}
            """

    context = f"DB Data: Name: {data.get('name')}, Tel: {data.get('phone')}, City: {data.get('city')}" if data else "New client, no history."

    prompt = f"""
            Role: Epiland Administrator. 
            Today is {today.strftime('%A, %d.%m.%Y')}.

            GOAL: Extract info and update JSON.
            If the user changes information (e.g., new city), update it. 
            Keep existing data from CONTEXT if not changed.

            CONTEXT: {context}
            HISTORY: {history}
            USER MESSAGE: "{userMessage}"
            
            {base_rules}
        """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt
        )

        if not response.text:
            raise ValueError("Empty response from AI")

        # Clean Markdown formatting from AI response to get pure JSON
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        res = json.loads(clean_text)

        #Calling Validate Number function

        phone = res['data'].get('phone')

        if phone:
            is_valid, validatedPhone = validateNumber(phone)

            if is_valid:
                res['data']['phone'] = validatedPhone

            else:
                res['data']['phone'] = None
                res['is_complete'] = False
                res['reply'] = f"Здається, номер телефону вказано невірно. {res['reply']}"

        # Calling Validate Data function

        date_params = res['data'].get('date_params')
        final_date = get_calculated_date(date_params)
        res['data']['date'] = final_date

        if not final_date:
            res['is_complete'] = False

        return res

    except Exception as e:
        print(f"AI/JSON Error: {e}")
        return {
            "reply": "Вибач, я трохи завис. Спробуй ще раз!",
            "is_complete": False,
            "data": {"name": None, "phone": None, "city": None, "date_params": None}
        }