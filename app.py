from flask import Flask, render_template,request, redirect
from datetime import datetime
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

# connection = sqlite3.connect("tracker.db")
# cursor = connection.cursor()

# cursor.execute("DELETE FROM tasks WHERE id BETWEEN 7 AND 16")

# connection.commit()
# connection.close()

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

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM tasks"
    )

    tasks = [list(task) for task in cursor.fetchall()]

    today = datetime.now().date()

    for task in tasks:
        if task[6]:
            task[6] = datetime.strptime(task[6],"%Y-%m-%d %H:%M:%S.%f").strftime("%d %b %Y, %I:%M %p")
        if task[4]:
            due_date = datetime.strptime(task[4], "%Y-%m-%d").date()
            if task[5] == 1 and due_date < today:
                task.append(True)
            else:
                task.append(False)

    connection.close()

    return render_template("index.html",tasks=tasks)

@app.route("/edit/<int:task_id>", methods=["GET","POST"])
def edit_task(task_id):

    if request.method == "POST":
        task = request.form["task"]
        subject = request.form["subject"]
        priority = request.form["priority"]
        due_date = request.form["due_date"]

        connection = get_db()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE tasks
            SET task=?, subject=?, priority=?, due_date=?
            WHERE id=?
            """,
            (task, subject, priority, due_date, task_id)
        )

        connection.commit()
        connection.close()

        return redirect("/")

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM tasks WHERE id=?",
        (task_id,)
    )

    task = cursor.fetchone()

    connection.close()

    return render_template("edit.html", task=task)


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    connection = get_db()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id=?",
        (task_id,)
    )

    connection.commit()
    connection.close()

    return redirect("/")

    
@app.route("/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    connection = get_db()
    cursor = connection.cursor()

    completed_at = datetime.now()

    cursor.execute(
        "UPDATE tasks SET status=2, completed_at=? WHERE id=?",(completed_at,task_id)
    )

    connection.commit()
    connection.close()

    return redirect("/")




init_db()

if __name__ == "__main__":
    app.run(debug=True)