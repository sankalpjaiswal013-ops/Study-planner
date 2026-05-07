import time
import json
import google.generativeai as genai
from datetime import datetime
from database import get_db_connection, get_setting
from utils import get_weak_strong_subjects

def get_context_for_ai(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT subject, topic, difficulty, due_date FROM tasks WHERE user_id=? AND completed=0", (user_id,))
    pending = c.fetchall()
    conn.close()
    
    pending_list = [{"subject": p["subject"], "topic": p["topic"], "difficulty": p["difficulty"], "due": p["due_date"]} for p in pending]
    
    scores, weak, average, strong = get_weak_strong_subjects(user_id)
    
    context = f"""
    Today's Date: {datetime.now().strftime("%Y-%m-%d")}
    Pending Tasks: {json.dumps(pending_list)}
    Weak Subjects (Score < 40): {[w['subject'] for w in weak]}
    Strong Subjects (Score > 70): {[s['subject'] for s in strong]}
    """
    return context

def generate_ai_response(user_id, prompt, chat_history):
    api_key = get_setting(user_id, "gemini_api_key", None)
    context = get_context_for_ai(user_id)
    
    system_prompt = f"""You are a highly motivating AI Study Assistant.
    Use the following student context to give personalized advice:
    {context}
    
    Keep responses concise, actionable, and encouraging.
    """
    
    if not api_key:
        # Fallback Mock AI if no API key is provided
        time.sleep(1.5) # Simulate processing
        
        if "analyze" in prompt.lower() or "weak" in prompt.lower():
            return "Based on your data, I see some weak subjects. You should focus your next study session on those to bring your scores up! Try breaking the difficult topics into smaller 25-minute Pomodoro sessions."
        elif "study today" in prompt.lower():
            return "Today, I recommend prioritizing your pending Hard tasks or tasks due very soon. Check your dashboard for the overdue tasks!"
        elif "plan" in prompt.lower():
            return "Here is a quick plan: 1. Do a 25-min Pomodoro on your weakest subject. 2. Take a 5 min break. 3. Tackle a medium priority pending task. You've got this!"
        elif "motivate" in prompt.lower():
            return "You are doing great! Every minute you spend studying is an investment in your future. Keep pushing forward, you can conquer these subjects!"
        else:
            return "I am a mock AI because no Gemini API key was provided in Settings. Please add a free Gemini API key to enable full AI chat functionality! In the meantime, I recommend checking your Analysis page."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # We will manually inject the context to avoid chat history object issues
        is_first_user_msg = True
        formatted_history = ""
        
        for msg in chat_history:
            if msg["role"] == "system":
                continue 
                
            role = "AI" if msg["role"] == "assistant" else "User"
            formatted_history += f"{role}: {msg['content']}\n\n"
            
        final_prompt = f"INSTRUCTIONS: {system_prompt}\n\nPREVIOUS CHAT HISTORY:\n{formatted_history}\n\nUSER MESSAGE: {prompt}"
                
        response = model.generate_content(final_prompt)
        
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            # Debugging: let's see what models are actually available to this API key
            try:
                available = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        available.append(m.name)
                return f"❌ Gemini API Error 404. The model was not found. However, your API key HAS access to these models: {', '.join(available)}. Please let me know this list so I can fix the code!"
            except Exception as e2:
                return f"❌ Gemini API Error: {error_msg} (Also failed to list models: {str(e2)})"
        return f"❌ Gemini API Error: {error_msg}. Please check your API key in settings."
