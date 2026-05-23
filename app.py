from flask import Flask
from bot import run_bot

app = Flask(__name__)

@app.route("/")
def home():

    return "Crypto bot is running."

@app.route("/run")
def run():

    run_bot()

    return "Bot executed successfully."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)