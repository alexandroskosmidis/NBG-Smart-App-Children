from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# --- CORS SETTINGS (Απαραίτητο για τη σύνδεση με React) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Στην παραγωγή βάλε το URL της React (π.χ. http://localhost:5173)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configs
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('models/gemini-flash-latest')

class NewGoalRequest(BaseModel):
    child_id: str
    item_name: str
    target_amount: float
    category: str

@app.post("/create-goal")
async def create_goal(request: NewGoalRequest):
    try:

        child_response = supabase.table("children").select("*").eq("id", request.child_id).execute()
        
        # Έλεγχος αν βρέθηκε το παιδί
        if not child_response.data:
            raise HTTPException(status_code=404, detail=f"Το παιδί με ID {request.child_id} δεν βρέθηκε στη βάση!")
            
        child = child_response.data[0] # Παίρνουμε το πρώτο (και μοναδικό) αποτέλεσμα
        
        # 1. Τραβάμε δεδομένα παιδιού & ορίων για το Context του AI
        child = supabase.table("children").select("*").eq("id", request.child_id).single().execute().data

        
        cap = supabase.table("spending_caps").select("*").eq("child_id", request.child_id).eq("category", request.category).execute().data
        
        current_savings = child.get("savings_balance", 0)
        cap_info = f"Όριο {request.category}: {cap[0]['limit_amount']}€" if cap else "Χωρίς συγκεκριμένο όριο."


        # Υπολογισμοί πριν το prompt για ακρίβεια
        missing_amount = request.target_amount - current_savings
        
        # Προτείνουμε έναν ρυθμό για να το πάρει σε 4 εβδομάδες (π.χ. 1 μήνα)
        weekly_rate = missing_amount / 4 if missing_amount > 0 else 0

        # Νέο "Data-Rich" Prompt
        prompt = f"""
        Είσαι ο Finny, ένας πανέξυπνος οικονομικός σύμβουλος για παιδιά {child['age']} ετών.
        Στόχος: {request.item_name} αξίας {request.target_amount}€.
        Ήδη αποταμιευμένα: {current_savings}€.
        Ποσό που λείπει: {missing_amount}€.
        Ρυθμός για στόχο σε 4 εβδομάδες: {weekly_rate:.2f}€/εβδομάδα.
        Πληροφορία ορίου: {cap_info}.

        ΟΔΗΓΙΑ: Απάντησε με ΜΙΑ πρόταση στα Ελληνικά (έως 20-25 λέξεις). 
        Πρέπει οπωσδήποτε να αναφέρεις ότι λείπουν {missing_amount}€ και να προτείνεις τον ρυθμό των {weekly_rate:.2f}€ την εβδομάδα, 
        συσχετίζοντάς το με το όριο {request.category} (π.χ. 'αν ξοδεύεις λιγότερα σε {request.category}...').
        """
        
        ai_response = model.generate_content(prompt).text.strip()


        # 3. Αποθήκευση στη βάση (Saving_goal table)
        goal_data = {
            "child_id": request.child_id,
            "item_name": request.item_name,
            "category": request.category,
            "target_amount": request.target_amount,
            "current_saved": current_savings,
            "ai_suggestion": ai_response
        }
        
        insert_result = supabase.table("saving_goals").insert(goal_data).execute()

        return {
            "status": "success",
            "goal": insert_result.data[0],
            "suggestion": ai_response
        }

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Κάτι πήγε στραβά με τη δημιουργία του στόχου.")



    

# Endpoint για να παίρνει το Frontend όλους τους στόχους του παιδιού
@app.get("/get-goals/{child_id}")
async def get_goals(child_id: str):
    goals = supabase.table("saving_goals").select("*").eq("child_id", child_id).execute()
    return goals.data

@app.get("/debug/children")
async def get_all_children():
    res = supabase.table("children").select("id, fullname").execute()
    return res.data