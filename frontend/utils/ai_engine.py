import re

def generate_mock_summary(text: str) -> str:
    """
    Simulates an AI analyzing clinical text. 
    In a real app, you would call OpenAI/Gemini API here.
    """
    if not text:
        return "No clinical text provided to analyze."
        
    # Extract potential symptoms (very basic mock logic)
    symptoms = re.findall(r'(pain|cough|fever|nausea|dizziness|fatigue)', text, re.IGNORECASE)
    unique_symptoms = list(set([s.lower() for s in symptoms]))
    
    summary = "### 🧠 AI Clinical Analysis\n"
    summary += f"**Analyzed Text Length:** {len(text)} characters\n\n"
    
    if unique_symptoms:
        summary += "**Identified Potential Symptoms:**\n"
        for s in unique_symptoms:
            summary += f"- {s.title()}\n"
    else:
        summary += "No obvious keywords found. Manual review recommended.\n"
        
    summary += "\n**Recommendation:** Correlate with patient's pre-visit snapshot and lab results."
    return summary