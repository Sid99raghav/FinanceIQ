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
import datetime
import requests
import shutil

# TODO: import functions https redirect
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# import functions from dbmgr
import sys
sys.path.append("lib")
import utils
import json
import genai_utils

"""
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session


DATABASE_URL = "sqlite:///./properties.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
"""

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
        profile = load_profile(email) or {
            "name": user.display_name,
            "email": email,
            "picture": user.picture,
        }

        # Check if role is missing
        if not profile.get("role"):
            save_profile(email, profile)  # Save the profile to ensure it's initialized
            return RedirectResponse(url="/edit-profile.html", status_code=302)

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

def get_data_path(type_):
    return os.path.join(DATA_DIR, f"{type_}.json")

def load_data(type_):
    path = get_data_path(type_)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def save_data(type_, data):
    path = get_data_path(type_)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

@app.post("/api/assets")
async def save_asset(item: dict = Body(...)):
    email = item.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    name = item.get("name")
    amount = item.get("amount")
    if not name or amount is None:
        raise HTTPException(status_code=400, detail="Asset name and amount required")
    assets = load_data("assets")
    user_assets = assets.get(email, [])
    user_assets.append({"name": name, "amount": amount})
    assets[email] = user_assets
    save_data("assets", assets)
    return {"ok": True}

@app.get("/api/assets")
async def get_assets(email: str):
    assets = load_data("assets")
    return assets.get(email, [])

@app.post("/api/incomes")
async def save_income(item: dict = Body(...)):
    email = item.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    source = item.get("source")
    amount = item.get("amount")
    if not source or amount is None:
        raise HTTPException(status_code=400, detail="Income source and amount required")
    incomes = load_data("incomes")
    user_incomes = incomes.get(email, [])
    user_incomes.append({"source": source, "amount": amount})
    incomes[email] = user_incomes
    save_data("incomes", incomes)
    return {"ok": True}

@app.get("/api/incomes")
async def get_incomes(email: str):
    incomes = load_data("incomes")
    return incomes.get(email, [])

@app.post("/api/expenses")
async def save_expense(item: dict = Body(...)):
    email = item.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    name = item.get("name")
    amount = item.get("amount")
    if not name or amount is None:
        raise HTTPException(status_code=400, detail="Expense name and amount required")
    expenses = load_data("expenses")
    user_expenses = expenses.get(email, [])
    user_expenses.append({"name": name, "amount": amount})
    expenses[email] = user_expenses
    save_data("expenses", expenses)
    return {"ok": True}

@app.get("/api/expenses")
async def get_expenses(email: str):
    expenses = load_data("expenses")
    return expenses.get(email, [])
