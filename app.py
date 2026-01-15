from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os
import re

# ===================== APP SETUP =====================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "feedback.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

app = Flask(__name__, static_folder="frontend", static_url_path="")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ===================== MODELS =====================

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(10))  # Positive / Negative only
    themes = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=func.now())

# ===================== RULE-BASED LOGIC =====================

POSITIVE = {"shiny", "elegant", "premium", "beautiful", "comfortable"}
NEGATIVE = {"tarnish", "dull", "heavy", "broke", "uncomfortable"}

THEMES = {
    "Comfort": {"light", "heavy", "fit", "wearable", "comfortable", "uncomfortable"},
    "Durability": {"broke", "strong", "quality", "fragile", "tarnish"},
    "Appearance": {"shiny", "dull", "design", "polish", "beautiful"}
}

WORD_RE = re.compile(r"\b[a-zA-Z']+\b")

def tokenize(text: str):
    return [w.lower() for w in WORD_RE.findall(text)]

# ---------- SENTIMENT (STRICT: POSITIVE / NEGATIVE ONLY) ----------

def analyze_sentiment(text: str) -> str:
    tokens = tokenize(text)
    pos = sum(t in POSITIVE for t in tokens)
    neg = sum(t in NEGATIVE for t in tokens)

    # Deterministic rule: ties go to Positive
    return "Positive" if pos >= neg else "Negative"

# ---------- THEME DETECTION ----------

def detect_themes(text: str):
    tokens = set(tokenize(text))
    return [theme for theme, keys in THEMES.items() if tokens & keys]

# ===================== INIT DATABASE =====================

def init_db():
    with app.app_context():
        db.create_all()
        if Product.query.count() == 0:
            db.session.add_all([
                Product(sku="RING001", name="Aurora Gold Ring"),
                Product(sku="EARR002", name="Luna Silver Earrings"),
                Product(sku="NECK003", name="Solstice Necklace")
            ])
            db.session.commit()

# ===================== ROUTES =====================

@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

# ---------- PRODUCTS ----------

@app.route("/api/products")
def products():
    return jsonify([
        {"id": p.id, "sku": p.sku, "name": p.name}
        for p in Product.query.all()
    ])

# ---------- SUBMIT FEEDBACK ----------

@app.route("/api/feedback", methods=["POST"])
def submit_feedback():
    data = request.json
    product = Product.query.filter_by(sku=data["product_sku"]).first()

    fb = Feedback(
        product_id=product.id,
        rating=data["rating"],
        text=data["text"],
        sentiment=analyze_sentiment(data["text"]),
        themes=",".join(detect_themes(data["text"]))
    )
    db.session.add(fb)
    db.session.commit()

    return jsonify({"status": "ok"})

# ---------- FETCH FEEDBACK FOR A PRODUCT ----------

@app.route("/api/feedback/<int:pid>")
def get_feedback(pid):
    rows = Feedback.query.filter_by(product_id=pid).all()
    return jsonify([
        {
            "rating": r.rating,
            "sentiment": r.sentiment,
            "text": r.text
        } for r in rows
    ])

# ---------- STATS (POSITIVE / NEGATIVE ONLY) ----------

@app.route("/api/stats/<int:pid>")
def stats(pid):
    sentiments = {
        "positive": Feedback.query.filter_by(product_id=pid, sentiment="Positive").count(),
        "negative": Feedback.query.filter_by(product_id=pid, sentiment="Negative").count()
    }

    themes = {
        theme: Feedback.query.filter(
            Feedback.product_id == pid,
            Feedback.themes.like(f"%{theme}%")
        ).count()
        for theme in THEMES
    }

    return jsonify({
        "sentiments": sentiments,
        "themes": themes
    })

# ===================== INSIGHTS (POSITIVE / NEGATIVE ASSUMPTION) =====================

@app.route("/api/insights/<int:pid>")
def insights(pid):
    stats_data = stats(pid).get_json()
    sentiments = stats_data["sentiments"]
    themes = stats_data["themes"]

    insights = []

    # Rule 1: Overall negative sentiment dominates
    if sentiments["negative"] > sentiments["positive"]:
        insights.append(
            "Overall customer sentiment is negative. Key issues should be investigated urgently."
        )

    # Rule 2: Durability complaints
    if themes["Durability"] > 0 and sentiments["negative"] >= sentiments["positive"]:
        insights.append(
            "Multiple durability-related complaints detected. Improve material strength and build quality."
        )

    # Rule 3: Comfort issues
    if themes["Comfort"] > 0 and sentiments["negative"] >= sentiments["positive"]:
        insights.append(
            "Comfort issues are frequently mentioned. Consider lighter and more wearable designs."
        )

    # Rule 4: Appearance praised (positive signal)
    if themes["Appearance"] > 0 and sentiments["positive"] > sentiments["negative"]:
        insights.append(
            "Appearance is positively received. Highlight design and finish in marketing."
        )

    if not insights:
        insights.append("Feedback is balanced. No strong actionable insight at this time.")

    return jsonify(insights)

# ===================== MAIN =====================

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
