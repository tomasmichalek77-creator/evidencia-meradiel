import sqlite3
import calendar as cal_module
from flask import Flask, request, jsonify, render_template, g
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "kalendar.db")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        db.executescript("""
            CREATE TABLE IF NOT EXISTS kolegovia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meno TEXT NOT NULL,
                farba TEXT NOT NULL DEFAULT '#4A90E2'
            );
            CREATE TABLE IF NOT EXISTS udalosti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nazov TEXT NOT NULL,
                datum TEXT NOT NULL,
                datum_do TEXT,
                cas_od TEXT,
                cas_do TEXT,
                popis TEXT,
                kolega_id INTEGER,
                FOREIGN KEY (kolega_id) REFERENCES kolegovia(id)
            );
        """)
        # migrate: add datum_do if missing
        cols = [r[1] for r in db.execute("PRAGMA table_info(udalosti)").fetchall()]
        if "datum_do" not in cols:
            db.execute("ALTER TABLE udalosti ADD COLUMN datum_do TEXT")
        db.commit()

        count = db.execute("SELECT COUNT(*) FROM kolegovia").fetchone()[0]
        if count == 0:
            db.executemany(
                "INSERT INTO kolegovia (meno, farba) VALUES (?, ?)",
                [
                    ("Ján Novák", "#2563EB"),
                    ("Mária Kováčová", "#DC2626"),
                    ("Peter Horváth", "#16A34A"),
                ],
            )
            db.commit()


@app.route("/")
def index():
    return render_template("index.html")


# ── kolegovia ─────────────────────────────────────────────────────────────────

@app.route("/api/kolegovia", methods=["GET"])
def get_kolegovia():
    rows = get_db().execute("SELECT * FROM kolegovia ORDER BY meno").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/kolegovia", methods=["POST"])
def add_kolega():
    data = request.get_json()
    if not data or not data.get("meno"):
        return jsonify({"error": "Meno je povinné"}), 400
    db = get_db()
    cur = db.execute(
        "INSERT INTO kolegovia (meno, farba) VALUES (?, ?)",
        (data["meno"].strip(), data.get("farba", "#2563EB")),
    )
    db.commit()
    return jsonify({"id": cur.lastrowid, "meno": data["meno"], "farba": data.get("farba", "#2563EB")}), 201


@app.route("/api/kolegovia/<int:kid>", methods=["DELETE"])
def delete_kolega(kid):
    db = get_db()
    db.execute("UPDATE udalosti SET kolega_id = NULL WHERE kolega_id = ?", (kid,))
    db.execute("DELETE FROM kolegovia WHERE id = ?", (kid,))
    db.commit()
    return jsonify({"ok": True})


# ── udalosti ──────────────────────────────────────────────────────────────────

@app.route("/api/udalosti", methods=["GET"])
def get_udalosti():
    rok = request.args.get("rok")
    mesiac = request.args.get("mesiac")
    db = get_db()
    if rok and mesiac:
        r, m = int(rok), int(mesiac)
        first_day = f"{r:04d}-{m:02d}-01"
        last_day_num = cal_module.monthrange(r, m)[1]
        last_day = f"{r:04d}-{m:02d}-{last_day_num:02d}"
        rows = db.execute(
            """SELECT u.*, k.meno as kolega_meno, k.farba as kolega_farba
               FROM udalosti u LEFT JOIN kolegovia k ON u.kolega_id = k.id
               WHERE u.datum <= ? AND COALESCE(u.datum_do, u.datum) >= ?
               ORDER BY u.datum, u.cas_od""",
            (last_day, first_day),
        ).fetchall()
    else:
        rows = db.execute(
            """SELECT u.*, k.meno as kolega_meno, k.farba as kolega_farba
               FROM udalosti u LEFT JOIN kolegovia k ON u.kolega_id = k.id
               ORDER BY u.datum, u.cas_od"""
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/udalosti", methods=["POST"])
def add_udalost():
    data = request.get_json()
    if not data or not data.get("nazov") or not data.get("datum"):
        return jsonify({"error": "Názov a dátum sú povinné"}), 400
    datum_do = data.get("datum_do") or None
    if datum_do and datum_do <= data["datum"]:
        datum_do = None
    db = get_db()
    cur = db.execute(
        "INSERT INTO udalosti (nazov, datum, datum_do, cas_od, cas_do, popis, kolega_id) VALUES (?,?,?,?,?,?,?)",
        (
            data["nazov"].strip(),
            data["datum"],
            datum_do,
            data.get("cas_od") or None,
            data.get("cas_do") or None,
            data.get("popis", "").strip() or None,
            data.get("kolega_id") or None,
        ),
    )
    db.commit()
    row = db.execute(
        """SELECT u.*, k.meno as kolega_meno, k.farba as kolega_farba
           FROM udalosti u LEFT JOIN kolegovia k ON u.kolega_id = k.id WHERE u.id=?""",
        (cur.lastrowid,),
    ).fetchone()
    return jsonify(dict(row)), 201


@app.route("/api/udalosti/<int:uid>", methods=["PUT"])
def update_udalost(uid):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Žiadne dáta"}), 400
    datum_do = data.get("datum_do") or None
    if datum_do and datum_do <= data.get("datum", ""):
        datum_do = None
    db = get_db()
    db.execute(
        "UPDATE udalosti SET nazov=?, datum=?, datum_do=?, cas_od=?, cas_do=?, popis=?, kolega_id=? WHERE id=?",
        (
            data.get("nazov", "").strip(),
            data.get("datum"),
            datum_do,
            data.get("cas_od") or None,
            data.get("cas_do") or None,
            data.get("popis", "").strip() or None,
            data.get("kolega_id") or None,
            uid,
        ),
    )
    db.commit()
    row = db.execute(
        """SELECT u.*, k.meno as kolega_meno, k.farba as kolega_farba
           FROM udalosti u LEFT JOIN kolegovia k ON u.kolega_id = k.id WHERE u.id=?""",
        (uid,),
    ).fetchone()
    return jsonify(dict(row))


@app.route("/api/udalosti/<int:uid>", methods=["DELETE"])
def delete_udalost(uid):
    db = get_db()
    db.execute("DELETE FROM udalosti WHERE id = ?", (uid,))
    db.commit()
    return jsonify({"ok": True})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5050, debug=False)
