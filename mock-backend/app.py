from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.post("/api/v1/auth/login")
def login():
    return jsonify({
        "access": "mock-access-token",
        "refresh": "mock-refresh-token",
    })

@app.get("/api/v1/users/self")
def me():
    return jsonify({
        "id": 1,
        "role": "CLIENT",
        "email": "test@test.pl",
        "first_name": "Jan",
        "surname": "Testowy",
    })

@app.get("/api/v1/patients")
def patients():
    return jsonify([
        {"id": 1, "name": "Jan", "surname": "Testowy", "birthday": "2000-01-01"},
        {"id": 2, "name": "Anna", "surname": "Testowa", "birthday": "2000-01-02"},
    ])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)