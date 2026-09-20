from flask import Flask, render_template,request
import sqlite3

app= Flask(__name__)

def get_db():
    return sqlite3.connect("tracker.db")

def init_db():
    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            subject TEXT,
            priority INTEGER,
            due_date DATE,
            status INTEGER DEFAULT 1,
            completed_at DATE
        )
    """)

    connection.commit()
    connection.close()

@app.route("/", methods=["GET","POST"])
def home():

    if request.method == "POST":
        task = request.form["task"]
        subject = request.form["subject"]
        priority = request.form["priority"]
        due_date = request.form["due_date"]

        connection = get_db()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO tasks (task, subject, priority, due_date) VALUES (?,?,?,?)", (task,subject,priority,due_date)
        )

        connection.commit()
        connection.close()

    return render_template("index.html")

    
    

init_db()

if __name__ == "__main__":
    app.run(debug=True)