
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3, os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret")

DB = os.environ.get("DATABASE_PATH", "carpool.db")
PEOPLE = ["BABU","VINAY","GOWDA","JHONY","NANDI","BALAJI","VIDYA"]
PASSWORDS = {
    "BABU":"babu123","VINAY":"vinay123","GOWDA":"gowda123","JHONY":"jhony123",
    "NANDI":"nandi123","BALAJI":"balaji123","VIDYA":"vidya123","ADMIN":"admin123"
}

def db():
    c=sqlite3.connect(DB)
    c.row_factory=sqlite3.Row
    return c

def init():
    c=db()
    c.execute("""CREATE TABLE IF NOT EXISTS entries(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trip_date TEXT NOT NULL,
        person TEXT NOT NULL,
        frozen INTEGER NOT NULL DEFAULT 0,
        UNIQUE(trip_date,person))""")
    c.execute("""CREATE TABLE IF NOT EXISTS days(
        trip_date TEXT PRIMARY KEY,
        frozen INTEGER NOT NULL DEFAULT 0)""")
    c.commit(); c.close()
init()

def login_required(f):
    @wraps(f)
    def w(*a,**k):
        if "user" not in session: return jsonify(error="Login required"),401
        return f(*a,**k)
    return w

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form.get("username","").strip().upper()
        p=request.form.get("password","")
        if u in PASSWORDS and PASSWORDS[u]==p:
            session["user"]=u
            return redirect(url_for("home"))
        return render_template("login.html",error="Invalid username or password")
    return render_template("login.html",error=None)

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("login"))

@app.route("/")
def home():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("index.html",user=session["user"],people=PEOPLE)

@app.route("/api/data")
@login_required
def data():
    c=db()
    rows=c.execute("SELECT trip_date,person FROM entries").fetchall()
    frozen={r["trip_date"] for r in c.execute("SELECT trip_date FROM days WHERE frozen=1")}
    out={}
    for r in rows: out.setdefault(r["trip_date"],[]).append(r["person"])
    c.close()
    return jsonify(entries=out,frozen=list(frozen),user=session["user"])

@app.route("/api/toggle",methods=["POST"])
@login_required
def toggle():
    d=request.json.get("date"); person=request.json.get("person")
    if not d or person not in PEOPLE: return jsonify(error="Invalid data"),400
    c=db()
    if c.execute("SELECT frozen FROM days WHERE trip_date=?",(d,)).fetchone():
        c.close(); return jsonify(error="Date is frozen"),403
    row=c.execute("SELECT id FROM entries WHERE trip_date=? AND person=?",(d,person)).fetchone()
    if row: c.execute("DELETE FROM entries WHERE id=?",(row["id"],))
    else: c.execute("INSERT INTO entries(trip_date,person) VALUES(?,?)",(d,person))
    c.commit(); c.close(); return jsonify(ok=True)

@app.route("/api/freeze",methods=["POST"])
@login_required
def freeze():
    d=request.json.get("date")
    c=db()
    c.execute("INSERT INTO days(trip_date,frozen) VALUES(?,1) ON CONFLICT(trip_date) DO UPDATE SET frozen=1",(d,))
    c.execute("UPDATE entries SET frozen=1 WHERE trip_date=?",(d,))
    c.commit(); c.close(); return jsonify(ok=True)

@app.route("/api/unfreeze",methods=["POST"])
@login_required
def unfreeze():
    if session["user"]!="ADMIN": return jsonify(error="Admin only"),403
    d=request.json.get("date"); c=db()
    c.execute("DELETE FROM days WHERE trip_date=?",(d,))
    c.execute("UPDATE entries SET frozen=0 WHERE trip_date=?",(d,))
    c.commit(); c.close(); return jsonify(ok=True)

@app.route("/api/cycles")
@login_required
def cycles():
    c=db()
    rows=c.execute("SELECT trip_date,person,id FROM entries WHERE frozen=1 ORDER BY trip_date,id").fetchall()
    counts={p:0 for p in PEOPLE}; cycles={}
    for r in rows:
        counts[r["person"]]+=1
        n=counts[r["person"]]
        cycles.setdefault(n,[]).append(r["person"])
    pending={}
    maxcycle=max(cycles.keys(),default=0)
    for n in range(1,maxcycle+1):
        done=set(cycles.get(n,[]))
        pending[n]=[p for p in PEOPLE if p not in done and counts[p] < n]
    c.close()
    return jsonify(cycles=cycles,pending=pending,counts=counts)

if __name__=="__main__":
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)
