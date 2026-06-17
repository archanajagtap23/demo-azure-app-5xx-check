"""
demo-azure-5xx-app — Stable v1
All endpoints return 200. Deployed first to establish the baseline.
"""
import os
import time
import json
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "version": "v1",
        "timestamp": int(time.time()),
    })


@app.route("/api/products")
def products():
    return jsonify([
        {"id": 1, "name": "Widget A", "price": 9.99,  "stock": 100},
        {"id": 2, "name": "Widget B", "price": 19.99, "stock": 50},
        {"id": 3, "name": "Widget C", "price": 4.99,  "stock": 200},
    ])


@app.route("/api/checkout", methods=["GET", "POST"])
def checkout():
    return jsonify({
        "order_id": f"ord-{int(time.time())}",
        "status": "confirmed",
        "message": "Order placed successfully",
        "estimated_delivery": "2-3 business days",
    })


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    return jsonify({"error": "Not found", "path": f"/{path}"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
