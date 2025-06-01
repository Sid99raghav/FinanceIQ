from fastapi import FastAPI, Query, HTTPException, Request, UploadFile, Form
from typing import List, Optional
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse, JSONResponse
import base64
import logging
from pydantic import BaseModel, validator, ValidationError
from pathlib import Path
import json
import os

# Configure logger
logger = logging.getLogger("financeiq")
logging.basicConfig(level=logging.INFO)

# TODO: import functions https redirect
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# import functions from dbmgr
import sys
sys.path.append("lib")
import json
import genai_utils

app = FastAPI(debug=True)

# TODO: https redirect
# app.add_middleware(HTTPSRedirectMiddleware)

# Mount the "site" folder directly to the root URL
#app.mount("/s", StaticFiles(directory="site", html=True), name="site")
# Mount the static directory
app.mount("/site", StaticFiles(directory="site"), name="site")

@app.get("/")
def serve_homepage():
    return FileResponse("site/index.html")

############# Logic for OAuth and SSO with Google ##############
## SSO with Google
from lib.google_sso import GoogleSSOManager
from fastapi import Request

# Initialize Google SSO Manager with the app instance
google_sso_manager = GoogleSSOManager(app=app, config_path="site/assets/js/sso.yaml")

@app.get("/google/login")
async def google_login():
    """Generate login URL and redirect"""
    try:
        return await google_sso_manager.get_login_redirect()
    except Exception as e:
        logging.error(f"Error generating login URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate login URL.")

@app.get("/google/callback")
async def google_callback(request: Request):
    """Process login response from Google and return user info"""
    try:
        user = await google_sso_manager.verify_and_process(request)

        # Log the user info
        logger.info(f"User logged in: {user.email}")

        # Set session data
        request.session["user"] = {
            "id": user.id,
            "email": user.email,
            "display_name": user.display_name,
            "picture": user.picture,
        }

        # Load or initialize the profile
        email = user.email

        # Helper functions for profile management
        PROFILE_DIR = os.path.join(DATA_DIR, "profiles")
        os.makedirs(PROFILE_DIR, exist_ok=True)

        def profile_path(email):
            safe_email = email.replace("@", "_at_").replace(".", "_dot_")
            return os.path.join(PROFILE_DIR, f"{safe_email}.json")

        def load_profile(email):
            path = profile_path(email)
            if os.path.exists(path):
                with open(path, "r") as f:
                    return json.load(f)
            return None

        def save_profile(email, profile):
            path = profile_path(email)
            with open(path, "w") as f:
                json.dump(profile, f, indent=2)

        profile = load_profile(email) or {
            "name": user.display_name,
            "email": email,
            "picture": user.picture,
        }

        # Check if role is missing
        if not profile.get("role"):
            save_profile(email, profile)  # Save the profile to ensure it's initialized
            return RedirectResponse(url="/", status_code=302)

        # Save the profile and redirect to the homepage
        save_profile(email, profile)
        return RedirectResponse(url="/", status_code=302)
    except Exception as e:
        logging.error(f"Error processing login response: {e}")
        raise HTTPException(status_code=500, detail="Failed to process login response.")
    
@app.get("/logout")
async def logout(request: Request):
    """Clear the session and log out the user"""
    request.session.clear()
    return RedirectResponse(url="/")

@app.get("/session")
async def get_session(request: Request):
    """Check if the user is logged in"""
    user = request.session.get("user")
    if user:
        return JSONResponse(content={"authenticated": True, "user": user})
    return JSONResponse(content={"authenticated": False})

@app.post("/api/plan")
async def plan(request: Request):
    """
    Receive assets, expenses, income_sources, goals, goal_period and return a GenAI-generated plan.
    """
    data = await request.json()
    # Compose a prompt for GenAI
    prompt = f"""
You are a financial advisor. Given the following user data, generate a detailed, actionable financial plan in markdown format.

Assets: {data.get('assets')}
Expenses: {data.get('expenses')}
Income Sources: {data.get('income_sources')}
Goals: {data.get('goals')}
Goal Time Period (years): {data.get('goal_period')}

The plan should include savings strategy, investment suggestions, and a timeline to achieve the goals.
"""
    response = genai_utils.gemini_chat_completion(prompt)
    plan = response if isinstance(response, str) else getattr(response, "text", str(response))
    return {"plan": plan}

from fastapi import Body

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
USERS_DATA_PATH = os.path.join(DATA_DIR, "users.json")

def default_user():
    return {
        "income": [],
        "assets": [],
        "expenses": [],
        "goals": [],
        "financial_plan": ""
    }

def load_users():
    if not os.path.exists(USERS_DATA_PATH):
        return {}
    with open(USERS_DATA_PATH, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_DATA_PATH, "w") as f:
        json.dump(users, f, indent=2)

@app.post("/api/assets")
# Sample input:
# {
#   "email": "user@example.com",
#   "name": "House",
#   "amount": 100000
# }
async def save_asset(item: dict = Body(...)):
    email = item.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    name = item.get("name")
    amount = item.get("amount")
    if not name or amount is None:
        raise HTTPException(status_code=400, detail="Asset name and amount required")
    users = load_users()
    user = users.get(email, default_user())
    user["assets"].append({"name": name, "amount": amount})
    users[email] = user
    save_users(users)
    return {"ok": True}

@app.get("/api/assets")
# Sample input: /api/assets?email=user@example.com
async def get_assets(email: str):
    users = load_users()
    user = users.get(email, {})
    return user.get("assets", [])

@app.post("/api/incomes")
# Sample input:
# {
#   "email": "user@example.com",
#   "source": "Salary",
#   "amount": 9000
# }
async def save_income(item: dict = Body(...)):
    email = item.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    source = item.get("source")
    amount = item.get("amount")
    if not source or amount is None:
        raise HTTPException(status_code=400, detail="Income source and amount required")
    users = load_users()
    user = users.get(email, default_user())
    user["income"].append({"name": source, "amount": amount})
    users[email] = user
    save_users(users)
    return {"ok": True}

@app.get("/api/incomes")
# Sample input: /api/incomes?email=user@example.com
async def get_incomes(email: str):
    users = load_users()
    user = users.get(email, {})
    return user.get("income", [])

@app.post("/api/expenses")
# Sample input:
# {
#   "email": "user@example.com",
#   "name": "Rent",
#   "amount": 2000
# }
async def save_expense(item: dict = Body(...)):
    email = item.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    name = item.get("name")
    amount = item.get("amount")
    if not name or amount is None:
        raise HTTPException(status_code=400, detail="Expense name and amount required")
    users = load_users()
    user = users.get(email, default_user())
    user["expenses"].append({"name": name, "amount": amount})
    users[email] = user
    save_users(users)
    return {"ok": True}

@app.get("/api/expenses")
# Sample input: /api/expenses?email=user@example.com
async def get_expenses(email: str):
    users = load_users()
    user = users.get(email, {})
    return user.get("expenses", [])

@app.post("/api/goals")
# Sample input:
# {
#   "email": "user@example.com",
#   "name": "Buy Car",
#   "amount": 15000,
#   "years": 3
# }
async def save_goal(item: dict = Body(...)):
    email = item.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    name = item.get("name")
    amount = item.get("amount")
    years = item.get("years")
    if not name or amount is None or years is None:
        raise HTTPException(status_code=400, detail="Goal name, amount, and years required")
    users = load_users()
    user = users.get(email, default_user())
    user["goals"].append({"name": name, "amount": amount, "years": years})
    users[email] = user
    save_users(users)
    return {"ok": True}

@app.get("/api/goals")
# Sample input: /api/goals?email=user@example.com
async def get_goals(email: str):
    users = load_users()
    user = users.get(email, {})
    return user.get("goals", [])

@app.post("/api/plan")
# Sample input:
# {
#   "email": "user@example.com",
#   "plan": "Your generated plan text here"
# }
async def save_financial_plan(item: dict = Body(...)):
    email = item.get("email")
    plan = item.get("plan")
    if not email or plan is None:
        raise HTTPException(status_code=400, detail="Email and plan required")
    users = load_users()
    user = users.get(email, default_user())
    user["financial_plan"] = plan
    users[email] = user
    save_users(users)
    return {"ok": True}

@app.get("/api/plan")
# Sample input: /api/plan?email=user@example.com
async def get_financial_plan(email: str):
    users = load_users()
    user = users.get(email, {})
    return {"financial_plan": user.get("financial_plan", "")}

@app.post("/api/plan/generate")
# Sample input:
# {
#   "email": "user@example.com"
# }
async def generate_financial_plan(item: dict = Body(...)):
    """
    Always generate a new financial plan and save it for the user.
    Uses values from the database. Generates plan even if some fields are missing.
    """
    return await generate_financial(item["email"])

async def generate_financial(email: str):
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    users = load_users()
    user = users.get(email)
    if not user:
        raise HTTPException(status_code=404, detail="User data not found")
    assets = user.get("assets", [])
    expenses = user.get("expenses", [])
    income = user.get("income", [])
    goals = user.get("goals", [])
    goal_period = goals[0]["years"] if goals and "years" in goals[0] else None

    prompt = f"""
You are a financial advisor. Given the following user data, generate a detailed, actionable financial plan in markdown format.
The amounts are in INR.

Assets: {assets}
Expenses: {expenses}
Income Sources: {income}
Goals: {goals}
Goal Time Period (years): {goal_period}

The plan should include savings strategy, investment suggestions, and a timeline to achieve the goals.
Please respond below infomation in proper tabular format only
1. Show how to achive goals, and how much to invest for each goal, in different investment instruments, amount (sip or lumpsum per month), timeline.
2. Monthly outflow should not exceed 80% of Monthly income. Consider inflation of 6% per year and loan interest of 10% per year. 
3. If not able to achieve goals, suggest how much income is required to achieve the goals.
"""
    logger.info(f"Generating financial plan for {email} with prompt: {prompt}")
    response = genai_utils.gemini_chat_completion(prompt, format="markdown")
    if not response:
        raise HTTPException(status_code=500, detail="Failed to generate financial plan")
    plan = response if isinstance(response, str) else getattr(response, "text", str(response))
    user["financial_plan"] = plan
    users[email] = user
    save_users(users)
    return {"financial_plan": plan}

@app.post("/api/plan/view")
# Sample input:
# {
#   "email": "user@example.com"
# }
async def view_financial_plan(item: dict = Body(...)):
    """
    View the saved plan if it exists, else generate, save, and return a new plan.
    Uses values from the database. Generates plan even if some fields are missing.
    """
    email = item.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    users = load_users()
    user = users.get(email)
    if not user:
        raise HTTPException(status_code=404, detail="User data not found")
    if user.get("financial_plan"):
        return {"financial_plan": user["financial_plan"]}
    return await generate_financial(email)

@app.post("/api/incomes/update")
async def update_income(item: dict = Body(...)):
    """
    Update an income entry for a user.
    Input: { "email": ..., "oldName": ..., "newName": ..., "amount": ... }
    """
    email = item.get("email")
    old_name = item.get("oldName")
    new_name = item.get("newName")
    amount = item.get("amount")
    if not email or not old_name or new_name is None or amount is None:
        raise HTTPException(status_code=400, detail="Email, oldName, newName, and amount required")
    users = load_users()
    user = users.get(email, default_user())
    updated = False
    for income in user["income"]:
        if income["name"] == old_name:
            income["name"] = new_name
            income["amount"] = amount
            updated = True
            break
    if not updated:
        raise HTTPException(status_code=404, detail="Income entry not found")
    users[email] = user
    save_users(users)
    return {"ok": True}

@app.post("/api/incomes/delete")
async def delete_income(item: dict = Body(...)):
    """
    Delete an income entry for a user.
    Input: { "email": ..., "name": ... }
    """
    email = item.get("email")
    name = item.get("name")
    if not email or not name:
        raise HTTPException(status_code=400, detail="Email and name required")
    users = load_users()
    user = users.get(email, default_user())
    before = len(user["income"])
    user["income"] = [inc for inc in user["income"] if inc["name"] != name]
    after = len(user["income"])
    users[email] = user
    save_users(users)
    return {"ok": True, "deleted": before - after}

@app.post("/api/assets/update")
async def update_asset(item: dict = Body(...)):
    """
    Update an asset entry for a user.
    Input: { "email": ..., "oldName": ..., "newName": ..., "amount": ... }
    """
    email = item.get("email")
    old_name = item.get("oldName")
    new_name = item.get("newName")
    amount = item.get("amount")
    if not email or not old_name or new_name is None or amount is None:
        raise HTTPException(status_code=400, detail="Email, oldName, newName, and amount required")
    users = load_users()
    user = users.get(email, default_user())
    updated = False
    for asset in user["assets"]:
        if asset["name"] == old_name:
            asset["name"] = new_name
            asset["amount"] = amount
            updated = True
            break
    if not updated:
        raise HTTPException(status_code=404, detail="Asset entry not found")
    users[email] = user
    save_users(users)
    return {"ok": True}

@app.post("/api/assets/delete")
async def delete_asset(item: dict = Body(...)):
    """
    Delete an asset entry for a user.
    Input: { "email": ..., "name": ... }
    """
    email = item.get("email")
    name = item.get("name")
    if not email or not name:
        raise HTTPException(status_code=400, detail="Email and name required")
    users = load_users()
    user = users.get(email, default_user())
    before = len(user["assets"])
    user["assets"] = [a for a in user["assets"] if a["name"] != name]
    after = len(user["assets"])
    users[email] = user
    save_users(users)
    return {"ok": True, "deleted": before - after}

@app.post("/api/expenses/update")
async def update_expense(item: dict = Body(...)):
    """
    Update an expense entry for a user.
    Input: { "email": ..., "oldName": ..., "newName": ..., "amount": ... }
    """
    email = item.get("email")
    old_name = item.get("oldName")
    new_name = item.get("newName")
    amount = item.get("amount")
    if not email or not old_name or new_name is None or amount is None:
        raise HTTPException(status_code=400, detail="Email, oldName, newName, and amount required")
    users = load_users()
    user = users.get(email, default_user())
    updated = False
    for expense in user["expenses"]:
        if expense["name"] == old_name:
            expense["name"] = new_name
            expense["amount"] = amount
            updated = True
            break
    if not updated:
        raise HTTPException(status_code=404, detail="Expense entry not found")
    users[email] = user
    save_users(users)
    return {"ok": True}

@app.post("/api/expenses/delete")
async def delete_expense(item: dict = Body(...)):
    """
    Delete an expense entry for a user.
    Input: { "email": ..., "name": ... }
    """
    email = item.get("email")
    name = item.get("name")
    if not email or not name:
        raise HTTPException(status_code=400, detail="Email and name required")
    users = load_users()
    user = users.get(email, default_user())
    before = len(user["expenses"])
    user["expenses"] = [e for e in user["expenses"] if e["name"] != name]
    after = len(user["expenses"])
    users[email] = user
    save_users(users)
    return {"ok": True, "deleted": before - after}

@app.post("/api/goals/update")
async def update_goal(item: dict = Body(...)):
    """
    Update a goal entry for a user.
    Input: { "email": ..., "oldName": ..., "newName": ..., "amount": ..., "years": ... }
    """
    email = item.get("email")
    old_name = item.get("oldName")
    new_name = item.get("newName")
    amount = item.get("amount")
    years = item.get("years")
    if not email or not old_name or new_name is None or amount is None or years is None:
        raise HTTPException(status_code=400, detail="Email, oldName, newName, amount, and years required")
    users = load_users()
    user = users.get(email, default_user())
    updated = False
    for goal in user["goals"]:
        if goal["name"] == old_name:
            goal["name"] = new_name
            goal["amount"] = amount
            goal["years"] = years
            updated = True
            break
    if not updated:
        raise HTTPException(status_code=404, detail="Goal entry not found")
    users[email] = user
    save_users(users)
    return {"ok": True}

@app.post("/api/goals/delete")
async def delete_goal(item: dict = Body(...)):
    """
    Delete a goal entry for a user.
    Input: { "email": ..., "name": ... }
    """
    email = item.get("email")
    name = item.get("name")
    if not email or not name:
        raise HTTPException(status_code=400, detail="Email and name required")
    users = load_users()
    user = users.get(email, default_user())
    before = len(user["goals"])
    user["goals"] = [g for g in user["goals"] if g["name"] != name]
    after = len(user["goals"])
    users[email] = user
    save_users(users)
    return {"ok": True, "deleted": before - after}