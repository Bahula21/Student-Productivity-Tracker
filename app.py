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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            topic TEXT,
            duration INTEGER,
            date DATE
        )
    """)

    connection.commit()
    connection.close()

def get_tasks(search, filter_subject, priority, status, sort):
    connection = get_db()
    cursor=connection.cursor()

    conditions = []
    values = []

    if search:
        conditions.append("task LIKE ?")
        values.append("%" + search + "%")

    if filter_subject:
        conditions.append("subject = ?")
        values.append(filter_subject)

    if priority:
        conditions.append("priority = ?")
        values.append(priority)

    if status:
        conditions.append("status = ?")
        values.append(status)

    if conditions:
        query = "SELECT * FROM tasks WHERE " + " AND ".join(conditions)
    else:
        query = "SELECT * FROM tasks"

    if sort == "due_asc":
        query += " ORDER BY due_date ASC"
    elif sort == "due_desc":
        query += " ORDER BY due_date DESC"
    elif sort == "pri_high_low":
        query += " ORDER BY priority DESC"
    elif sort == "pri_low_high":
        query += " ORDER BY priority ASC"
    elif sort == "newest":
        query += " ORDER BY id DESC"
    elif sort == "oldest":
        query += "  ORDER BY id ASC"

    cursor.execute(query, values)


    tasks = [list(task) for task in cursor.fetchall()]

    connection.close()

    return tasks



@app.route("/", methods=["GET","POST"])
def home():

    search = request.args.get("search", "")
    filter_subject = request.args.get("subject", "")
    priority = request.args.get("priority", "")
    status = request.args.get("status", "")
    sort = request.args.get("sort", "")
    
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

    
    cursor.execute("SELECT DISTINCT subject FROM tasks WHERE subject IS NOT NULL AND subject != ''")
    subjects = [row[0] for row in cursor.fetchall()]

    today = datetime.now().date()

    tasks = get_tasks(search, filter_subject, priority, status, sort)

    for task in tasks:
        if task[6]:
            task[6] = datetime.strptime(task[6],"%Y-%m-%d %H:%M:%S.%f").strftime("%d %b %Y, %I:%M %p")
        if task[4]:
            due_date = datetime.strptime(task[4], "%Y-%m-%d").date()
            if task[5] == 1 and due_date < today:
                task.append(True)
            else:
                task.append(False)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status=1")
    pending_tasks = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status=2")
    completed_tasks = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE status=1 AND due_date < ?",
        (today,)
    )

    overdue_tasks = cursor.fetchone()[0]

    connection.close()

    return render_template(
        "index.html",
        tasks=tasks,
        subjects=subjects,
        total_tasks=total_tasks,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
        overdue_tasks=overdue_tasks,
        filter_subject=filter_subject,
        priority=priority,
        status=status,
        search=search,
        sort=sort

    )   

@app.route("/study-sessions", methods=["GET","POST"])
def study_sessions():
    if request.method == "POST":
        subject = request.form["subject"]
        topic = request.form["topic"]
        duration = request.form["duration"]
        date = request.form["date"]

        connection = get_db()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO study_sessions(subject,topic,duration,date) 
            VALUES(?,?,?,?)
            """,(subject,topic,duration,date)
        )

        connection.commit()
        connection.close()

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM study_sessions")

    sessions = cursor.fetchall()

    connection.close()

    return render_template("study_sessions.html",sessions=sessions)

@app.route("/delete-session/<int:session_id>", methods=["POST"])
def delete_session(session_id):
    connection = get_db()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM study_sessions WHERE id=?",
        (session_id,)
    )

    connection.commit()
    connection.close()

    return redirect("/study-sessions")


@app.route("/edit-session/<int:session_id>", methods=["GET", "POST"])
def edit_session(session_id):
    if request.method == "POST":
        subject = request.form["subject"]
        topic = request.form["topic"]
        duration = request.form["duration"]
        date = request.form["date"]
        connection = get_db()
        cursor = connection.cursor()

        connection = get_db()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE study_sessions
            SET subject=?, topic=?, duration=?, date=?
            WHERE id=?
            """,
            (subject, topic, duration, date, session_id)
        )

        connection.commit()
        connection.close()

        return redirect("/study-sessions")

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM study_sessions WHERE id=?",
        (session_id,)
    )

    session = cursor.fetchone()

    connection.close()

    return render_template("edit_session.html", session=session)

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