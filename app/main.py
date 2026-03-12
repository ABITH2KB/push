from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory "database"
tasks = []
next_id = 1


@app.route("/")
def home():
    return jsonify({"message": "Task API is running 🚀", "version": "1.0.0"})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify({"tasks": tasks, "count": len(tasks)})


@app.route("/tasks", methods=["POST"])
def create_task():
    global next_id
    data = request.get_json()

    if not data or "title" not in data:
        return jsonify({"error": "title is required"}), 400

    task = {
        "id": next_id,
        "title": data["title"],
        "done": False,
    }
    tasks.append(task)
    next_id += 1
    return jsonify(task), 201


@app.route("/tasks/<int:task_id>", methods=["PATCH"])
def update_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    if "done" in data:
        task["done"] = data["done"]
    if "title" in data:
        task["title"] = data["title"]

    return jsonify(task)


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    tasks = [t for t in tasks if t["id"] != task_id]
    return jsonify({"message": f"Task {task_id} deleted"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)