# Feedback Hub – Giva

Feedback Hub is a small web application built for a jewelry brand like **Giva** to collect customer reviews, analyze them using **simple rule-based logic**, and present meaningful insights on a dashboard.

The project intentionally avoids AI/ML models and focuses on **clarity, explainability, and business logic**, exactly as required in the problem statement.

---

## 1. Problem Overview

Customers leave reviews on products such as rings, earrings, and necklaces.  
The business wants to understand:

- Whether feedback is **positive or negative**
- What customers care about most (comfort, durability, appearance)
- What **actionable insights** can be derived from customer feedback

---

## 2. High-Level Architecture

The application follows a simple **client–server architecture**:

Frontend (Browser)  
→ fetch APIs  
Backend (Flask)  
→ SQLite Database  

- Frontend: HTML, Bootstrap, JavaScript, Chart.js  
- Backend: Flask + Flask-SQLAlchemy  
- Database: SQLite  

The frontend never accesses the database directly.  
All communication happens via REST APIs.

---

## 3. Backend Design

### Data Models

Product  
- id  
- sku  
- name  

Feedback  
- product_id  
- rating  
- review text  
- sentiment  
- themes  
- timestamp  

Each feedback entry is linked to a product and stores both the raw review and the analyzed results.

---

## 4. Feedback Submission Flow

1. User submits product, rating, and review text  
2. Backend analyzes sentiment using rule-based logic  
3. Themes are detected using keyword matching  
4. Feedback is stored in the database  
5. Aggregated data is served to the frontend via APIs  

---

## 5. Rule-Based Sentiment Analysis

No external NLP or AI libraries are used.

Positive words:  
shiny, elegant, premium, beautiful, comfortable  

Negative words:  
tarnish, dull, heavy, broke, uncomfortable  

Logic:
- Tokenize review text into lowercase words
- Count positive and negative word matches
- If positive ≥ negative → **Positive**
- Else → **Negative**

This ensures deterministic classification as required.

---

## 6. Theme Detection Logic

Themes are detected using predefined keyword groups.

Comfort:  
light, heavy, fit, wearable  

Durability:  
broke, fragile, strong, quality  

Appearance:  
shiny, dull, design, polish  

A single review can belong to multiple themes.

Example:  
“The necklace looks shiny but feels heavy”  
→ Appearance + Comfort  

---

## 7. Insights Generation

Insights are generated using **simple business rules** based on aggregated data.

Examples:
- More negative sentiment → investigate issues
- Frequent durability complaints → improve material quality
- Comfort issues dominate → consider lighter designs
- Positive appearance feedback → highlight design in marketing

This simulates how a business analyst interprets customer feedback.

---

## 8. Frontend Functionality

Feedback Submission:
- Product dropdown (predefined)
- Rating (1–5)
- Review text
- Submit button

Dashboard:
- Pie chart: Positive vs Negative sentiment
- Bar chart: Theme counts
- Feedback history table
- “Generate Insights” button (explicit user action)

All updates happen dynamically using JavaScript fetch calls without page reload.

---

## 9. REST APIs

GET /api/products  
→ Load product dropdown  

POST /api/feedback  
→ Submit feedback  

GET /api/feedback/<product_id>  
→ Fetch feedback history  

GET /api/stats/<product_id>  
→ Sentiment and theme statistics  

GET /api/insights/<product_id>  
→ Generate insights  

---

## 10. How to Run Locally

python -m venv venv  
venv\Scripts\activate   (Windows)  
pip install -r requirements.txt  
python app.py  

Open in browser:  
http://127.0.0.1:5000  

---

## 11. Deployment

The application is deployed on **Render** using:
- Gunicorn as the production server
- GitHub-based continuous deployment
- Environment-based port configuration

Live demo (example):  
https://feedback-hub-giva.onrender.com  

---

## 12. Design Decisions

- Rule-based sentiment chosen for transparency
- Predefined products to focus on logic
- SQLite for lightweight persistence
- Explicit “Generate Insights” button for better UX

---

## 13. Future Improvements

- Authentication
- Pagination and search
- Optional ML-based sentiment analysis
- Persistent production database (PostgreSQL)

---

## 14. Key Takeaway

Feedback Hub demonstrates how **simple, explainable logic** can extract meaningful business insights from customer reviews without complex AI models.

