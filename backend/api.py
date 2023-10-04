from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/get")
def grab_images():
    return "grabbing images..."


@app.route("/send", methods=["POST"])
def send_images():
    return "sending images..."
