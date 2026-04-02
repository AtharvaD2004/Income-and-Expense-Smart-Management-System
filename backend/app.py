"""
I&E Manager — Flask Backend
Run: python app.py
"""
from flask import Flask
from flask_cors import CORS
from config import Config
from models.database import db
from routes.auth_routes import auth_bp
from routes.transaction_routes import transaction_bp
from routes.analytics_routes import analytics_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    app.register_blueprint(auth_bp,        url_prefix="/api/auth")
    app.register_blueprint(transaction_bp, url_prefix="/api/transactions")
    app.register_blueprint(analytics_bp,   url_prefix="/api/analytics")
    with app.app_context():
        db.create_all()
        print("✅ Database ready.")
    return app

app = create_app()

@app.route("/")
def index():
    return {"status": "running", "app": "I&E Manager API v1.0"}

@app.errorhandler(404)
def not_found(e):
    return {"error": "Endpoint not found."}, 404

@app.errorhandler(500)
def server_error(e):
    return {"error": "Internal server error."}, 500

if __name__ == "__main__":
    print("🚀 I&E Manager Backend running at http://localhost:5000")
    app.run(debug=True, port=5000)
