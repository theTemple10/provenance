"""Flask REST API for item management with authentication."""

from flask import Flask, jsonify, request

from .models import ItemStore
from .routes_auth import auth_bp
from .middleware import token_required

app = Flask(__name__)
store = ItemStore()
app.register_blueprint(auth_bp)


@app.route("/items", methods=["GET"])
def list_items():
    return jsonify({"items": store.list_all(), "count": store.count()})


@app.route("/items/<item_id>", methods=["GET"])
def get_item(item_id: str):
    item = store.get(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item.to_dict())


@app.route("/items", methods=["POST"])
@token_required
def create_item():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Name is required"}), 400
    item = store.create(
        name=data["name"],
        description=data.get("description", ""),
        price=data.get("price", 0.0),
    )
    return jsonify(item.to_dict()), 201


@app.route("/items/<item_id>", methods=["DELETE"])
@token_required
def delete_item(item_id: str):
    if store.delete(item_id):
        return jsonify({"message": "Item deleted"})
    return jsonify({"error": "Item not found"}), 404


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
