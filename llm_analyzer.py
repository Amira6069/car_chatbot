import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class LLMAnalyzer:
    """
    Uses Groq's Llama-3.1-70B to analyze user queries about cars.
    Extracts intent and entities to query the database intelligently.
    Integrated with existing project structure.
    """
    
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key or api_key == 'your_groq_api_key_here':
            raise ValueError("⚠️ Please set your GROQ_API_KEY in the .env file!")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        
        print(f"✅ LLM Analyzer initialized with Groq {self.model}")
    
    def analyze_query(self, user_text):
        """
        Analyzes user query and returns structured intent + entities.
        
        Returns:
            dict: {
                'intent': str,
                'entities': {...}
            }
        """
        
        prompt = f"""You are a car database query analyzer. Analyze this user question and extract structured information.

User question: "{user_text}"

Database columns available:
- Make (e.g., toyota, bmw, honda, mercedes-benz, ford, chevrolet)
- Model (e.g., camry, civic, m6, c-class, mustang, cruze)
- Year (1990-2017)
- Engine HP (horsepower)
- Engine Cylinders
- Transmission Type (automatic, manual)
- Vehicle Size (compact, midsize, large)
- Vehicle Style (sedan, suv, coupe, wagon, hatchback, minivan, pickup)
- city mpg (fuel efficiency in city)
- highway MPG (fuel efficiency on highway)
- MSRP (price in USD)

Analyze and return ONLY a JSON object with this structure:
{{
    "intent": "search|compare|specs|list_all",
    "entities": {{
        "make": "brand name or null",
        "model": "model name or null", 
        "models_to_compare": ["model1", "model2"] or null,
        "min_price": number or null,
        "max_price": number or null,
        "vehicle_style": "suv|sedan|coupe|wagon|hatchback|pickup|minivan or null",
        "fuel_efficiency": true if user asks about MPG/fuel/gas consumption,
        "min_year": number or null,
        "max_year": number or null,
        "transmission": "automatic|manual or null"
    }}
}}

Intent definitions:
- "search": User wants to find specific cars (e.g., "find me a toyota", "I want an SUV under 30k")
- "compare": User wants to compare 2+ cars (e.g., "compare bmw m6 to toyota previa")
- "specs": User asks about specific car specs (e.g., "how much fuel does honda civic consume")
- "list_all": User wants to see all cars of a type (e.g., "show me all SUVs")

Important rules:
- Convert brand names to lowercase (BMW → bmw, Mercedes → mercedes-benz, Mercedes-Benz → mercedes-benz)
- For price: "under X" → max_price=X, "between X and Y" → min_price=X + max_price=Y, "over X" → min_price=X
- Convert 'k' and 'm' suffixes to numbers (e.g. 5k -> 5000, 1.5m -> 1500000)
- For fuel questions: set fuel_efficiency=true
- Return ONLY valid JSON, no explanations

Examples:
"Find me a Toyota under $30k" → {{"intent": "search", "entities": {{"make": "toyota", "max_price": 30000}}}}
"I want all SUVs" → {{"intent": "list_all", "entities": {{"vehicle_style": "suv"}}}}
"Compare BMW M6 to Toyota Previa" → {{"intent": "compare", "entities": {{"models_to_compare": ["m6", "previa"]}}}}
"How much fuel does Honda Civic consume" → {{"intent": "specs", "entities": {{"make": "honda", "model": "civic", "fuel_efficiency": true}}}}
"Mercedes between 20k and 50k" → {{"intent": "search", "entities": {{"make": "mercedes-benz", "min_price": 20000, "max_price": 50000}}}}

Now analyze: "{user_text}"
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise JSON generator. Return only valid JSON, no markdown, no explanations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean up response
            if result_text.startswith('```'):
                lines = result_text.split('\n')
                json_lines = [l for l in lines if not l.strip().startswith('```')]
                result_text = '\n'.join(json_lines)
            
            result = json.loads(result_text)
            
            print(f"🧠 LLM Analysis: intent={result.get('intent')}, entities={result.get('entities')}")
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
            print(f"Response was: {result_text}")
            return {
                'intent': 'search',
                'entities': {}
            }
        except Exception as e:
            print(f"❌ LLM Error: {e}")
            return {
                'intent': 'error',
                'error': str(e),
                'entities': {}
            }