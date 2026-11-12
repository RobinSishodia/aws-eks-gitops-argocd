from flask import Flask
import os
import socket

app = Flask(__name__)


@app.route("/")
def home():
    version = os.getenv("APP_VERSION", "v1")
    return (
        "<h1>GitOps demo - built by Jenkins</h1>"
        f"<p>Version: {version}</p>"
        f"<p>Served by: {socket.gethostname()}</p>"
    )


@app.route("/healthz")
def healthz():
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
