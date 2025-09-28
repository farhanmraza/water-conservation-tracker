from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB_NAME = "water_usage.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            amount REAL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        amount = float(request.form["amount"])
        date = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO usage (date, amount) VALUES (?, ?)", (date, amount))
        conn.commit()
        conn.close()
        return redirect(url_for("history"))
    return render_template("index.html")

@app.route("/history")
def history():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT date, amount FROM usage ORDER BY date DESC")
    data = c.fetchall()
    conn.close()

    if data:
        amounts = [row[1] for row in data]
        avg_usage = sum(amounts) / len(amounts)
        latest = data[0][1]
        if latest > avg_usage:
            tip = "Your usage is above average. Try shorter showers or fixing leaks!"
        else:
            tip = "Great job! You're conserving water efficiently."
    else:
        avg_usage, tip = None, None

    return render_template("history.html", data=data, avg_usage=avg_usage, tip=tip)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
