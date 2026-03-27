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
        # 1. Τραβάμε δεδομένα παιδιού (Μία φορά, σωστά)
        child_res = supabase.table("children").select("*").eq("id", request.child_id).execute()
        if not child_res.data:
            raise HTTPException(status_code=404, detail="Το παιδί δεν βρέθηκε.")
        
        child = child_res.data[0]
        
        # 2. Τραβάμε spending caps
        cap_res = supabase.table("spending_caps").select("*").eq("child_id", request.child_id).eq("category", request.category).execute()
        cap_data = cap_res.data
        
        current_savings = child.get("savings_balance", 0)
        cap_info = f"Όριο {request.category}: {cap_data[0]['limit_amount']}€" if cap_data else "Δεν υπάρχει συγκεκριμένο όριο για αυτή την κατηγορία."

        # 3. Υπολογισμοί
        missing_amount = request.target_amount - current_savings
        # Υπολογίζουμε μηνιαίο ρυθμό για να φτάσει το στόχο σε 3 μήνες
        monthly_rate = missing_amount / 3 if missing_amount > 0 else 0

        # 4. Εμπλουτισμένο Prompt
        prompt = f"""
        Είσαι ο Finny, ένας πανέξυπνος οικονομικός σύμβουλος για παιδιά {child['age']} ετών.
        Στόχος: {request.item_name} αξίας {request.target_amount}€.
        Λείπουν: {missing_amount}€.
        Μηνιαίος ρυθμός (για 3 μήνες): {monthly_rate:.2f}€/μήνα.
        Πληροφορία ορίου: {cap_info}.

        ΟΔΗΓΙΑ: Απάντησε ΑΥΣΤΗΡΑ σε δύο προτάσεις στα Ελληνικά:
        1. Στην πρώτη πρόταση, ανέφερε ότι λείπουν {missing_amount}€ και πες τη γνώμη σου αν η τιμή των {request.target_amount}€ είναι λογική για ένα {request.item_name}.
        2. Στη δεύτερη πρόταση, πρότεινε να αποταμιεύει {monthly_rate:.2f}€ το μήνα για να το έχει σε 3 μήνες, συνδέοντάς το με το {cap_info}.
        """
        
        ai_response = model.generate_content(prompt).text.strip()

        # 5. Αποθήκευση στη βάση
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
            "suggestion": ai_response,
            "calculation": {
                "missing": missing_amount,
                "monthly_needed": round(monthly_rate, 2)
            }
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Μοντέλο για το POST request (Δημιουργία νέου ορίου)
class SpendingCapCreate(BaseModel):
    parent_id: str
    child_id: str
    category: str
    limit_amount: float
    period: str
    

# Endpoint για να παίρνει το Frontend όλους τους στόχους του παιδιού
@app.get("/get-goals/{child_id}")
async def get_goals(child_id: str):
    goals = supabase.table("saving_goals").select("*").eq("child_id", child_id).execute()
    return goals.data

@app.get("/debug/children") 
async def get_all_children():
    res = supabase.table("children").select("id, fullname").execute()
    return res.data


# --- ENDPOINTS ΓΙΑ ΤΟ PARENT PAGE ---

@app.get("/api/parents/{parent_id}")
def get_parent_profile(parent_id: str):
    response = supabase.table("parents").select("*").eq("id", parent_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Δεν βρέθηκε ο γονέας")
    return response.data[0]

@app.get("/api/parents/{parent_id}/caps")
def get_parent_caps(parent_id: str):
    response = supabase.table("spending_caps").select("*").eq("parent_id", parent_id).execute()
    return response.data

@app.post("/api/caps")
def create_spending_cap(cap: SpendingCapCreate):
    response = supabase.table("spending_caps").insert([cap.dict()]).execute()
    return response.data[0]


# --- ENDPOINTS ΓΙΑ TRANSACTIONS & GOALS ---

@app.get("/api/children/{child_id}/transactions")
def get_transactions(child_id: str):
    response = supabase.table("transactions").select("*").eq("child_id", child_id).order("inserted_at", desc=True).execute()
    return response.data

@app.get("/api/children/{child_id}/goals")
def get_goals(child_id: str):
    response = supabase.table("saving_goals").select("*").eq("child_id", child_id).order("inserted_at", desc=True).execute()
    return response.data