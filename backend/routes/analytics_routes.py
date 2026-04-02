from flask import Blueprint, request, jsonify
from models.database import Transaction
from utils.auth_utils import login_required
from utils.analytics import get_full_analytics, get_summary, get_expense_by_category, get_bar_chart, get_monthly_trend, get_insights, get_health_score, get_top_categories

analytics_bp = Blueprint("analytics", __name__)

def _txns(user):
    return Transaction.query.filter_by(user_id=user.id).order_by(Transaction.date.desc()).all()

@analytics_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard(u): return jsonify(get_full_analytics(_txns(u))), 200

@analytics_bp.route("/summary", methods=["GET"])
@login_required
def summary(u): return jsonify(get_summary(_txns(u))), 200

@analytics_bp.route("/pie", methods=["GET"])
@login_required
def pie(u): return jsonify(get_expense_by_category(_txns(u))), 200

@analytics_bp.route("/bar", methods=["GET"])
@login_required
def bar(u): return jsonify(get_bar_chart(_txns(u))), 200

@analytics_bp.route("/trend", methods=["GET"])
@login_required
def trend(u):
    months = min(24, max(1, int(request.args.get("months", 6))))
    return jsonify(get_monthly_trend(_txns(u), months)), 200

@analytics_bp.route("/insights", methods=["GET"])
@login_required
def insights(u): return jsonify({"insights": get_insights(_txns(u))}), 200

@analytics_bp.route("/health", methods=["GET"])
@login_required
def health(u): return jsonify(get_health_score(_txns(u))), 200

@analytics_bp.route("/top-categories", methods=["GET"])
@login_required
def top_cats(u):
    limit = int(request.args.get("limit", 5))
    return jsonify(get_top_categories(_txns(u), limit)), 200
