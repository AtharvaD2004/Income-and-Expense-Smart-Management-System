"""
utils/analytics.py  —  Pandas-powered analytics engine
Every chart and insight in the dashboard is computed here.
"""
import pandas as pd

def to_df(transactions):
    if not transactions:
        return pd.DataFrame(columns=["id","description","amount","category","type","date"])
    rows = [{"id": t.id, "description": t.description, "amount": float(t.amount),
             "category": t.category, "type": t.type, "date": pd.to_datetime(t.date),
             "created_at": t.created_at} for t in transactions]
    df = pd.DataFrame(rows)
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df

# ── 1. Summary totals ─────────────────────────────────────────────────
def get_summary(transactions):
    df  = to_df(transactions)
    inc = float(df[df["type"] == "income"]["amount"].sum())     if not df.empty else 0
    exp = float(df[df["type"] == "expense"]["amount"].sum())    if not df.empty else 0
    inv = float(df[df["type"] == "investment"]["amount"].sum()) if not df.empty else 0
    bal = inc - exp - inv
    rate = round(((inc - exp - inv) / inc) * 100, 1) if inc > 0 else 0
    return {
        "total_income":      round(inc, 2),
        "total_expense":     round(exp, 2),
        "total_investment":  round(inv, 2),
        "net_balance":       round(bal, 2),
        "savings_rate":      rate,
        "transaction_count": len(df)
    }

# ── 2. Expense by category (pie chart) ───────────────────────────────
def get_expense_by_category(transactions):
    df = to_df(transactions)
    if df.empty: return []
    exp = df[df["type"] == "expense"]
    if exp.empty: return []
    g = exp.groupby("category")["amount"].sum().reset_index()
    g.columns = ["category", "amount"]
    g = g.sort_values("amount", ascending=False)
    total = g["amount"].sum()
    g["percentage"] = ((g["amount"] / total) * 100).round(1)
    return g.to_dict("records")

# ── 3. Monthly trend (line chart) ─────────────────────────────────────
def get_monthly_trend(transactions, months=6):
    df = to_df(transactions)
    if df.empty: return []
    pivot = df.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0).reset_index()
    for col in ["income", "expense", "investment"]:
        if col not in pivot.columns:
            pivot[col] = 0
    pivot = pivot.sort_values("month").tail(months)
    return [{"month": str(r["month"]),
             "income":     round(float(r.get("income", 0)), 2),
             "expense":    round(float(r.get("expense", 0)), 2),
             "investment": round(float(r.get("investment", 0)), 2)}
            for _, r in pivot.iterrows()]

# ── 4. Bar chart data ─────────────────────────────────────────────────
def get_bar_chart(transactions):
    s = get_summary(transactions)
    return {"labels": ["Income", "Expense", "Investment"],
            "values": [s["total_income"], s["total_expense"], s["total_investment"]],
            "colors": ["#1D9E75", "#D85A30", "#534AB7"]}

# ── 5. Top categories ─────────────────────────────────────────────────
def get_top_categories(transactions, limit=5):
    cats = get_expense_by_category(transactions)[:limit]
    for i, c in enumerate(cats): c["rank"] = i + 1
    return cats

# ── 6. Financial insights (behavioral analysis) ───────────────────────
def get_insights(transactions):
    df      = to_df(transactions)
    summary = get_summary(transactions)
    msgs    = []
    if df.empty or summary["total_income"] == 0:
        return ["Add some transactions to see your personalized insights!"]
    rate = summary["savings_rate"]
    if rate >= 30:   msgs.append(f"Excellent! You are saving {rate}% of your income. Keep it up!")
    elif rate >= 20: msgs.append(f"Good! Savings rate is {rate}%. Push above 30% for better security.")
    elif rate >= 0:  msgs.append(f"Savings rate is {rate}%. Try cutting discretionary spending.")
    else:            msgs.append(f"Alert: You are spending more than you earn. Review expenses now.")

    inv_rate = round((summary["total_investment"] / summary["total_income"]) * 100, 1) if summary["total_income"] > 0 else 0
    if inv_rate >= 20:   msgs.append(f"Great investing habit! You invest {inv_rate}% of your income.")
    elif inv_rate > 0:   msgs.append(f"You invest {inv_rate}% of income. Aim for 20% for long-term wealth.")
    else:                msgs.append("No investments yet. Consider starting a SIP or mutual fund.")

    cats = get_expense_by_category(transactions)
    if cats and cats[0]["percentage"] > 40:
        msgs.append(f"{cats[0]['category']} is {cats[0]['percentage']}% of your expenses. Consider budgeting it.")

    monthly = get_monthly_trend(transactions, months=3)
    if len(monthly) >= 2:
        change = ((monthly[-1]["expense"] - monthly[-2]["expense"]) / monthly[-2]["expense"] * 100) if monthly[-2]["expense"] > 0 else 0
        if change > 15:   msgs.append(f"Expenses rose {round(change, 1)}% vs last month. Watch your spending.")
        elif change < -15: msgs.append(f"Expenses dropped {round(abs(change), 1)}% vs last month. Well done!")
    return msgs

# ── 7. Health score ───────────────────────────────────────────────────
def get_health_score(transactions):
    s = get_summary(transactions)
    if s["total_income"] == 0:
        return {"score": 0, "grade": "N/A", "label": "No data", "breakdown": {}}
    savings_score    = min(40, max(0, s["savings_rate"] * 1.33))
    inv_rate         = (s["total_investment"] / s["total_income"]) * 100 if s["total_income"] > 0 else 0
    investment_score = min(30, max(0, inv_rate * 1.5))
    df               = to_df(transactions)
    n_cats           = len(df[df["type"] == "expense"]["category"].unique()) if not df.empty else 0
    spending_score   = max(0, 30 - n_cats * 2)
    score = min(100, max(0, round(savings_score + investment_score + spending_score)))
    grade, label = (("A","Excellent") if score>=80 else ("B","Good") if score>=65 else ("C","Average") if score>=50 else ("D","Needs Work") if score>=35 else ("F","Poor"))
    return {"score": score, "grade": grade, "label": label,
            "breakdown": {"savings": round(savings_score), "investment": round(investment_score), "spending_control": round(spending_score)}}

# ── 8. Full dashboard (one call) ──────────────────────────────────────
def get_full_analytics(transactions):
    return {
        "summary":             get_summary(transactions),
        "expense_by_category": get_expense_by_category(transactions),
        "monthly_trend":       get_monthly_trend(transactions),
        "bar_chart":           get_bar_chart(transactions),
        "top_categories":      get_top_categories(transactions),
        "insights":            get_insights(transactions),
        "health_score":        get_health_score(transactions)
    }
