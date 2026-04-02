import re
from datetime import datetime
from models.database import TRANSACTION_TYPES, CATEGORIES

def validate_register(d):
    name  = (d.get("name") or "").strip()
    email = (d.get("email") or "").strip()
    pw    = d.get("password") or ""
    if not name or len(name) < 2:           return False, "Name must be at least 2 characters."
    if not re.match(r"^\S+@\S+\.\S+$", email): return False, "Invalid email address."
    if len(pw) < 6:                          return False, "Password must be at least 6 characters."
    return True, ""

def validate_login(d):
    if not d.get("email") or not d.get("password"): return False, "Email and password required."
    return True, ""

def validate_transaction(d):
    desc   = (d.get("description") or "").strip()
    amount = d.get("amount")
    cat    = (d.get("category") or "").strip()
    t      = (d.get("type") or "").strip().lower()
    date   = d.get("date")
    if not desc:                         return False, "Description is required."
    try:
        amount = float(amount)
        if amount <= 0: raise ValueError()
    except (TypeError, ValueError):      return False, "Amount must be a positive number."
    if t not in TRANSACTION_TYPES:       return False, f"Type must be: {', '.join(TRANSACTION_TYPES)}."
    if cat not in CATEGORIES.get(t, []): return False, f"Invalid category '{cat}' for type '{t}'."
    try:
        if isinstance(date, str): datetime.strptime(date, "%Y-%m-%d")
    except ValueError:                   return False, "Date must be YYYY-MM-DD."
    return True, ""
