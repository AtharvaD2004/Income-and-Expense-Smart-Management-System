import io, csv
from datetime import datetime
from flask import Blueprint, request, jsonify, make_response
from models.database import db, Transaction, TRANSACTION_TYPES, CATEGORIES
from utils.auth_utils import login_required
from utils.validators import validate_transaction

transaction_bp = Blueprint("transactions", __name__)

@transaction_bp.route("/", methods=["GET"])
@login_required
def get_all(current_user):
    q = Transaction.query.filter_by(user_id=current_user.id)
    # Filters
    if t := request.args.get("type"):
        if t in TRANSACTION_TYPES: q = q.filter_by(type=t)
    if c := request.args.get("category"):
        q = q.filter_by(category=c)
    if df := request.args.get("date_from"):
        try: q = q.filter(Transaction.date >= datetime.strptime(df, "%Y-%m-%d").date())
        except ValueError: return jsonify({"error": "date_from must be YYYY-MM-DD."}), 400
    if dt := request.args.get("date_to"):
        try: q = q.filter(Transaction.date <= datetime.strptime(dt, "%Y-%m-%d").date())
        except ValueError: return jsonify({"error": "date_to must be YYYY-MM-DD."}), 400
    # Sort
    sorts = {"date_desc": Transaction.date.desc(), "date_asc": Transaction.date.asc(),
             "amount_desc": Transaction.amount.desc(), "amount_asc": Transaction.amount.asc()}
    q = q.order_by(sorts.get(request.args.get("sort", "date_desc"), Transaction.date.desc()))
    # Pagination
    try:
        page  = max(1, int(request.args.get("page", 1)))
        limit = max(1, min(200, int(request.args.get("limit", 50))))
    except ValueError:
        page, limit = 1, 50
    total = q.count()
    txns  = q.offset((page - 1) * limit).limit(limit).all()
    return jsonify({"transactions": [t.to_dict() for t in txns], "total": total, "page": page, "pages": (total + limit - 1) // limit}), 200

@transaction_bp.route("/", methods=["POST"])
@login_required
def create(current_user):
    data = request.get_json()
    if not data: return jsonify({"error": "JSON required."}), 400
    ok, err = validate_transaction(data)
    if not ok: return jsonify({"error": err}), 400
    txn = Transaction(
        user_id=current_user.id, description=data["description"].strip(),
        amount=float(data["amount"]), category=data["category"].strip(),
        type=data["type"].strip().lower(), date=datetime.strptime(data["date"], "%Y-%m-%d").date()
    )
    db.session.add(txn); db.session.commit()
    return jsonify({"message": "Transaction added.", "transaction": txn.to_dict()}), 201

@transaction_bp.route("/<int:txn_id>", methods=["GET"])
@login_required
def get_one(current_user, txn_id):
    txn = Transaction.query.filter_by(id=txn_id, user_id=current_user.id).first()
    if not txn: return jsonify({"error": "Transaction not found."}), 404
    return jsonify({"transaction": txn.to_dict()}), 200

@transaction_bp.route("/<int:txn_id>", methods=["PUT"])
@login_required
def update(current_user, txn_id):
    txn = Transaction.query.filter_by(id=txn_id, user_id=current_user.id).first()
    if not txn: return jsonify({"error": "Transaction not found."}), 404
    data = request.get_json() or {}
    merged = {"description": data.get("description", txn.description),
              "amount":      data.get("amount",      txn.amount),
              "category":    data.get("category",    txn.category),
              "type":        data.get("type",        txn.type),
              "date":        data.get("date",        txn.date.isoformat())}
    ok, err = validate_transaction(merged)
    if not ok: return jsonify({"error": err}), 400
    txn.description = merged["description"].strip()
    txn.amount      = float(merged["amount"])
    txn.category    = merged["category"].strip()
    txn.type        = merged["type"].strip().lower()
    txn.date        = datetime.strptime(merged["date"], "%Y-%m-%d").date()
    db.session.commit()
    return jsonify({"message": "Transaction updated.", "transaction": txn.to_dict()}), 200

@transaction_bp.route("/<int:txn_id>", methods=["DELETE"])
@login_required
def delete(current_user, txn_id):
    txn = Transaction.query.filter_by(id=txn_id, user_id=current_user.id).first()
    if not txn: return jsonify({"error": "Transaction not found."}), 404
    db.session.delete(txn); db.session.commit()
    return jsonify({"message": "Deleted."}), 200

@transaction_bp.route("/export", methods=["GET"])
@login_required
def export_csv(current_user):
    txns   = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    output = io.StringIO()
    w      = csv.writer(output)
    w.writerow(["ID", "Date", "Description", "Type", "Category", "Amount (INR)"])
    for t in txns: w.writerow([t.id, t.date.isoformat(), t.description, t.type, t.category, t.amount])
    resp = make_response(output.getvalue())
    resp.headers["Content-Type"]        = "text/csv"
    resp.headers["Content-Disposition"] = "attachment; filename=transactions.csv"
    return resp

@transaction_bp.route("/categories", methods=["GET"])
def categories():
    return jsonify({"types": TRANSACTION_TYPES, "categories": CATEGORIES}), 200
