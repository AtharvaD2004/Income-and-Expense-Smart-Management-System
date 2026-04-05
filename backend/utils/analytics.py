"""
utils/analytics.py
Pure Python analytics — NO pandas, NO numpy.
Does everything the old pandas version did using only built-in Python.
This works on ANY Python version, ANY server, zero installation issues.
"""

from collections import defaultdict


# ── helper ────────────────────────────────────────────────────────────
def _round2(v):
    return round(float(v), 2)


# ── 1. Summary ────────────────────────────────────────────────────────
def get_summary(transactions):
    inc = sum(t.amount for t in transactions if t.type == "income")
    exp = sum(t.amount for t in transactions if t.type == "expense")
    inv = sum(t.amount for t in transactions if t.type == "investment")
    bal = inc - exp - inv
    rate = round(((inc - exp - inv) / inc) * 100, 1) if inc > 0 else 0
    return {
        "total_income":      _round2(inc),
        "total_expense":     _round2(exp),
        "total_investment":  _round2(inv),
        "net_balance":       _round2(bal),
        "savings_rate":      rate,
        "transaction_count": len(transactions)
    }


# ── 2. Expense by category (pie chart) ───────────────────────────────
def get_expense_by_category(transactions):
    cat_map = defaultdict(float)
    for t in transactions:
        if t.type == "expense":
            cat_map[t.category] += t.amount

    if not cat_map:
        return []

    total = sum(cat_map.values())
    result = [
        {
            "category":   cat,
            "amount":     _round2(amt),
            "percentage": round((amt / total) * 100, 1)
        }
        for cat, amt in cat_map.items()
    ]
    return sorted(result, key=lambda x: x["amount"], reverse=True)


# ── 3. Monthly trend (line chart) ─────────────────────────────────────
def get_monthly_trend(transactions, months=6):
    month_map = defaultdict(lambda: {"income": 0.0, "expense": 0.0, "investment": 0.0})

    for t in transactions:
        month_key = t.date.strftime("%Y-%m")
        month_map[month_key][t.type] += t.amount

    sorted_months = sorted(month_map.keys())[-months:]

    return [
        {
            "month":      m,
            "income":     _round2(month_map[m]["income"]),
            "expense":    _round2(month_map[m]["expense"]),
            "investment": _round2(month_map[m]["investment"])
        }
        for m in sorted_months
    ]


# ── 4. Bar chart data ─────────────────────────────────────────────────
def get_bar_chart(transactions):
    s = get_summary(transactions)
    return {
        "labels": ["Income", "Expense", "Investment"],
        "values": [s["total_income"], s["total_expense"], s["total_investment"]],
        "colors": ["#1D9E75", "#D85A30", "#534AB7"]
    }


# ── 5. Top categories ─────────────────────────────────────────────────
def get_top_categories(transactions, limit=5):
    cats = get_expense_by_category(transactions)[:limit]
    for i, c in enumerate(cats):
        c["rank"] = i + 1
    return cats


# ── 6. Smart financial insights ───────────────────────────────────────
def get_insights(transactions):
    summary = get_summary(transactions)
    msgs = []

    if not transactions or summary["total_income"] == 0:
        return ["Add some transactions to see your personalized insights!"]

    rate = summary["savings_rate"]
    if rate >= 30:
        msgs.append(f"Excellent! You are saving {rate}% of your income. Keep it up!")
    elif rate >= 20:
        msgs.append(f"Good! Savings rate is {rate}%. Push above 30% for better security.")
    elif rate >= 0:
        msgs.append(f"Savings rate is {rate}%. Try cutting discretionary spending.")
    else:
        msgs.append("Alert: You are spending more than you earn. Review expenses now.")

    inv_rate = round((summary["total_investment"] / summary["total_income"]) * 100, 1)
    if inv_rate >= 20:
        msgs.append(f"Great investing habit! You invest {inv_rate}% of your income.")
    elif inv_rate > 0:
        msgs.append(f"You invest {inv_rate}% of income. Aim for 20% for long-term wealth.")
    else:
        msgs.append("No investments yet. Consider starting a SIP or mutual fund.")

    cats = get_expense_by_category(transactions)
    if cats and cats[0]["percentage"] > 40:
        msgs.append(
            f"{cats[0]['category']} is {cats[0]['percentage']}% of your expenses. "
            f"Consider setting a budget for this category."
        )

    monthly = get_monthly_trend(transactions, months=3)
    if len(monthly) >= 2:
        prev = monthly[-2]["expense"]
        last = monthly[-1]["expense"]
        if prev > 0:
            change = round(((last - prev) / prev) * 100, 1)
            if change > 15:
                msgs.append(f"Expenses rose {change}% vs last month. Watch your spending.")
            elif change < -15:
                msgs.append(f"Expenses dropped {abs(change)}% vs last month. Well done!")

    return msgs


# ── 7. Health score ───────────────────────────────────────────────────
def get_health_score(transactions):
    s = get_summary(transactions)
    if s["total_income"] == 0:
        return {"score": 0, "grade": "N/A", "label": "No data", "breakdown": {}}

    savings_score    = min(40, max(0, s["savings_rate"] * 1.33))
    inv_rate         = (s["total_investment"] / s["total_income"]) * 100
    investment_score = min(30, max(0, inv_rate * 1.5))

    expense_cats     = len(set(t.category for t in transactions if t.type == "expense"))
    spending_score   = max(0, 30 - expense_cats * 2)

    score = min(100, max(0, round(savings_score + investment_score + spending_score)))

    if score >= 80:   grade, label = "A", "Excellent"
    elif score >= 65: grade, label = "B", "Good"
    elif score >= 50: grade, label = "C", "Average"
    elif score >= 35: grade, label = "D", "Needs Work"
    else:             grade, label = "F", "Poor"

    return {
        "score": score,
        "grade": grade,
        "label": label,
        "breakdown": {
            "savings":          round(savings_score),
            "investment":       round(investment_score),
            "spending_control": round(spending_score)
        }
    }


# ── 8. Full dashboard (all in one call) ───────────────────────────────
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
