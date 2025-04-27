from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Dummy data for leads
DUMMY_LEADS = [
    {
        "name": "John Doe",
        "company": "Acme Inc.",
        "score": 87,
        "summary": "High potential",
        "market_signal": "Positive news",
        "win_probability": 75,
        "estimated_revenue": 50000,
        "recommended_action": "Move to Contract Stage",
        "automation_status": "Scheduled",
        "coaching_tip": "Leverage urgency"
    },
    {
        "name": "Jane Smith",
        "company": "Beta Corp.",
        "score": 92,
        "summary": "Decision maker engaged",
        "market_signal": "New funding",
        "win_probability": 82,
        "estimated_revenue": 120000,
        "recommended_action": "Send Proposal",
        "automation_status": "Completed",
        "coaching_tip": "Highlight ROI"
    },
    {
        "name": "Alice Johnson",
        "company": "Gamma LLC",
        "score": 68,
        "summary": "Needs follow-up",
        "market_signal": "Neutral",
        "win_probability": 55,
        "estimated_revenue": 30000,
        "recommended_action": "Schedule Call",
        "automation_status": "Pending",
        "coaching_tip": "Personalize outreach"
    }
]

@app.route('/get_leads', methods=['GET'])
def get_leads():
    return jsonify(DUMMY_LEADS)

@app.route('/optimize_pipeline', methods=['POST'])
def optimize_pipeline():
    return jsonify({"message": "Pipeline optimized successfully"})

@app.route('/automate_actions', methods=['POST'])
def automate_actions():
    return jsonify({"message": "Automation completed successfully"})

@app.route('/generate_coaching', methods=['POST'])
def generate_coaching():
    # Return dummy coaching tips for each lead in the posted data, or a generic message if no data
    leads = request.get_json(silent=True)
    if isinstance(leads, list):
        for lead in leads:
            lead["coaching_tip"] = "Keep momentum high"
        return jsonify(leads)
    return jsonify({"message": "Coaching tips generated successfully"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
