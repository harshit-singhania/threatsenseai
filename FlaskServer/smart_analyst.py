import os
import google.generativeai as genai
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

class SmartAnalyst:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GOOGLE_API_KEY/GEMINI_API_KEY not found in environment variables.")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')

    def generate_report(self, image_path, detected_label, person_count):
        """
        Generates a security analyst report for a given frame.
        """
        if not self.model:
            return {
                "summary": "AI Analyst unavailable (Missing API Key)",
                "severity_score": 0,
                "actions": ["Check server configuration"]
            }

        prompt = f"""
        You are an elite security analyst monitoring a surveillance feed. 
        A computer vision system has detected a potential threat.
        
        **Detection Data:**
        - Primary Detection: {detected_label}
        - People Count: {person_count}
        
        **Your Task:**
        Analyze the provided image frame and the detection data.
        1. VALIDATE: Is this actually a threat? (Context matters: A knife in a kitchen is normal, a knife in a crowd is a threat).
        2. EXPLAIN: Write a 1-sentence situational summary.
        3. SCORE: Assign a Severity Score from 1 (Safe) to 10 (Critical).
        4. RECOMMEND: List 3 specific actionable steps for security personnel.
        
        **Output Format:**
        Return ONLY valid JSON with this structure:
        {{
            "summary": "One sentence summary...",
            "severity_score": 8,
            "actions": ["Step 1", "Step 2", "Step 3"]
        }}
        """

        try:
            # Upload the file to Gemini
            myfile = genai.upload_file(image_path)
            
            # Generate content
            result = self.model.generate_content([myfile, prompt])
            
            # extract text response
            response_text = result.text
            
            # Clean up cleanup response to ensure JSON
            # Sometimes models add markdown code blocks
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            import json
            return json.loads(response_text)

        except Exception as e:
            print(f"Smart Analyst Error: {e}")
            return {
                "summary": f"Analysis failed: {str(e)}",
                "severity_score": 0,
                "actions": ["Manual review required"]
            }

    def analyze_scene(self, image_path):
        """
        Thinking Agent: Classifies scene and counts people when Vision Agent is uncertain.
        """
        if not self.model:
             return {"classification": "Normal", "people_count": 0, "analyst_report": None}

        prompt = """
        You are an advanced visual security agent.
        Analyze this image STRICTLY for the following disasters: 'Wildfire', 'Earthquake', 'Flood'.
        
        Task:
        1. Classify the image into ONE of these categories: ['Wildfire', 'Earthquake', 'Flood', 'Normal'].
           - Use 'Normal' if none of the specific disasters are clearly visible.
        2. Count the number of visible people.
        3. If a disaster is detected, provide a short 1-sentence summary and a severity score (1-10).
        
        Output format (JSON ONLY):
        {
            "classification": "Flood", 
            "people_count": 2,
            "summary": "...",
            "severity_score": 8
        }
        """
        
        try:
            myfile = genai.upload_file(image_path)
            result = self.model.generate_content([myfile, prompt])
            response_text = result.text.replace("```json", "").replace("```", "").strip()
            
            import json
            data = json.loads(response_text)
            
            # Normalize keys just in case
            cls = data.get("classification", "Normal")
            if cls not in ["Wildfire", "Earthquake", "Flood", "Normal"]:
                cls = "Normal"
            
            # Construct standard report structure if disaster detected
            report = None
            if cls != "Normal":
                report = {
                    "summary": data.get("summary", "Disaster detected by Thinking Agent"),
                    "severity_score": data.get("severity_score", 5),
                    "actions": ["Verify camera feed", "Deploy response team"]
                }
            
            return {
                "classification": cls,
                "people_count": data.get("people_count", 0),
                "analyst_report": report
            }

        except Exception as e:
            print(f"Thinking Agent Error: {e}")
            return {"classification": "Normal", "people_count": 0, "analyst_report": None}

# Singleton instance
analyst = SmartAnalyst()
