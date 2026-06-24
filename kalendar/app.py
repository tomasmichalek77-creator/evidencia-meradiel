import json
import sqlite3
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
            CREATE TABLE IF NOT EXISTS zakaznici (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nazov TEXT NOT NULL,
                ico TEXT
            );
            CREATE TABLE IF NOT EXISTS meradla (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nazov TEXT NOT NULL,
                inv TEXT
            );
            CREATE TABLE IF NOT EXISTS udalosti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                typ TEXT,
                nazov TEXT,
                datum TEXT NOT NULL,
                datum_do TEXT,
                cas_od TEXT,
                cas_do TEXT,
                kolega_ids TEXT DEFAULT '[]',
                zakaznik_id INTEGER,
                meradla_ids TEXT DEFAULT '[]',
                auto_znacka TEXT,
                auto_spz TEXT,
                dohlad_typ TEXT,
                miesto TEXT,
                popis TEXT,
                FOREIGN KEY (zakaznik_id) REFERENCES zakaznici(id)
            );
        """)

        # column migrations for existing databases
        cols = {r[1] for r in db.execute("PRAGMA table_info(udalosti)").fetchall()}
        for col, col_type in [
            ("typ", "TEXT"),
            ("kolega_ids", "TEXT DEFAULT '[]'"),
            ("zakaznik_id", "INTEGER"),
            ("meradla_ids", "TEXT DEFAULT '[]'"),
            ("auto_znacka", "TEXT"),
            ("auto_spz", "TEXT"),
            ("dohlad_typ", "TEXT"),
            ("miesto", "TEXT"),
        ]:
            if col not in cols:
                db.execute(f"ALTER TABLE udalosti ADD COLUMN {col} {col_type}")

        # migrate single kolega_id -> kolega_ids JSON array
        if "kolega_id" in cols:
            db.execute("""
                UPDATE udalosti
                SET kolega_ids = json_array(kolega_id)
                WHERE kolega_id IS NOT NULL
                  AND (kolega_ids IS NULL OR kolega_ids = '[]')
            """)

        db.commit()

        # seed default workers on first run
        if db.execute("SELECT COUNT(*) FROM kolegovia").fetchone()[0] == 0:
            db.executemany(
                "INSERT INTO kolegovia (meno, farba) VALUES (?, ?)",
                [
                    ("Michálek", "#2563EB"),
                    ("Kolaja",   "#DC2626"),
                    ("Pokorný",  "#16A34A"),
                    ("Hatala",   "#D97706"),
                ],
            )
            db.commit()


def ev_json(row):
    d = dict(row)
    return {
        "id":         d["id"],
        "typ":        d["typ"] or "ine",
        "nazov":      d["nazov"],
        "datum":      d["datum"],
        "datumDo":    d["datum_do"],
        "casOd":      d["cas_od"],
        "casDo":      d["cas_do"],
        "kolegaIds":  json.loads(d["kolega_ids"] or "[]"),
        "zakaznikId": d["zakaznik_id"],
        "meradlaIds": json.loads(d["meradla_ids"] or "[]"),
        "autoZnacka": d["auto_znacka"],
        "autoSpz":    d["auto_spz"],
        "dohladTyp":  d["dohlad_typ"],
        "miesto":     d["miesto"],
        "popis":      d["popis"],
    }


def ev_params(d):
    datum_do = d.get("datumDo") or None
    if datum_do and datum_do <= (d.get("datum") or ""):
        datum_do = None
    return (
        d.get("typ") or "ine",
        (d.get("nazov") or "").strip() or None,
        d.get("datum"),
        datum_do,
        d.get("casOd") or None,
        d.get("casDo") or None,
        json.dumps(d.get("kolegaIds") or []),
        d.get("zakaznikId") or None,
        json.dumps(d.get("meradlaIds") or []),
        (d.get("autoZnacka") or "").strip() or None,
        (d.get("autoSpz") or "").strip().upper() or None,
        d.get("dohladTyp") or None,
        (d.get("miesto") or "").strip() or None,
        (d.get("popis") or "").strip() or None,
    )


@app.route("/")
def index():
    return render_template("index.html")


# ── kolegovia ──────────────────────────────────────────────────────────────────

@app.route("/api/kolegovia", methods=["GET"])
def get_kolegovia():
    rows = get_db().execute("SELECT * FROM kolegovia ORDER BY id").fetchall()
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
    return jsonify({"id": cur.lastrowid, "meno": data["meno"].strip(),
                    "farba": data.get("farba", "#2563EB")}), 201


@app.route("/api/kolegovia/<int:kid>", methods=["DELETE"])
def delete_kolega(kid):
    db = get_db()
    db.execute("DELETE FROM kolegovia WHERE id = ?", (kid,))
    db.commit()
    return jsonify({"ok": True})


# ── zakaznici ──────────────────────────────────────────────────────────────────

@app.route("/api/zakaznici", methods=["GET"])
def get_zakaznici():
    rows = get_db().execute("SELECT * FROM zakaznici ORDER BY nazov").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/zakaznici", methods=["POST"])
def add_zakaznik():
    data = request.get_json()
    if not data or not data.get("nazov"):
        return jsonify({"error": "Názov je povinný"}), 400
    db = get_db()
    cur = db.execute(
        "INSERT INTO zakaznici (nazov, ico) VALUES (?, ?)",
        (data["nazov"].strip(), (data.get("ico") or "").strip() or None),
    )
    db.commit()
    return jsonify({"id": cur.lastrowid, "nazov": data["nazov"].strip(),
                    "ico": (data.get("ico") or "").strip() or None}), 201


@app.route("/api/zakaznici/<int:zid>", methods=["DELETE"])
def delete_zakaznik(zid):
    db = get_db()
    db.execute("UPDATE udalosti SET zakaznik_id = NULL WHERE zakaznik_id = ?", (zid,))
    db.execute("DELETE FROM zakaznici WHERE id = ?", (zid,))
    db.commit()
    return jsonify({"ok": True})


# ── meradla ────────────────────────────────────────────────────────────────────

@app.route("/api/meradla", methods=["GET"])
def get_meradla():
    rows = get_db().execute("SELECT * FROM meradla ORDER BY nazov").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/meradla", methods=["POST"])
def add_meradlo():
    data = request.get_json()
    if not data or not data.get("nazov"):
        return jsonify({"error": "Názov je povinný"}), 400
    db = get_db()
    cur = db.execute(
        "INSERT INTO meradla (nazov, inv) VALUES (?, ?)",
        (data["nazov"].strip(), (data.get("inv") or "").strip() or None),
    )
    db.commit()
    return jsonify({"id": cur.lastrowid, "nazov": data["nazov"].strip(),
                    "inv": (data.get("inv") or "").strip() or None}), 201


@app.route("/api/meradla/<int:mid>", methods=["DELETE"])
def delete_meradlo(mid):
    db = get_db()
    db.execute("DELETE FROM meradla WHERE id = ?", (mid,))
    db.commit()
    return jsonify({"ok": True})


# ── udalosti ───────────────────────────────────────────────────────────────────

@app.route("/api/udalosti", methods=["GET"])
def get_udalosti():
    rows = get_db().execute(
        "SELECT * FROM udalosti ORDER BY datum, cas_od"
    ).fetchall()
    return jsonify([ev_json(r) for r in rows])


@app.route("/api/udalosti", methods=["POST"])
def add_udalost():
    data = request.get_json()
    if not data or not data.get("datum"):
        return jsonify({"error": "Dátum je povinný"}), 400
    db = get_db()
    cur = db.execute(
        """INSERT INTO udalosti
           (typ,nazov,datum,datum_do,cas_od,cas_do,kolega_ids,zakaznik_id,
            meradla_ids,auto_znacka,auto_spz,dohlad_typ,miesto,popis)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        ev_params(data),
    )
    db.commit()
    row = db.execute("SELECT * FROM udalosti WHERE id=?", (cur.lastrowid,)).fetchone()
    return jsonify(ev_json(row)), 201


@app.route("/api/udalosti/<int:uid>", methods=["PUT"])
def update_udalost(uid):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Žiadne dáta"}), 400
    db = get_db()
    db.execute(
        """UPDATE udalosti SET
           typ=?,nazov=?,datum=?,datum_do=?,cas_od=?,cas_do=?,kolega_ids=?,
           zakaznik_id=?,meradla_ids=?,auto_znacka=?,auto_spz=?,dohlad_typ=?,miesto=?,popis=?
           WHERE id=?""",
        ev_params(data) + (uid,),
    )
    db.commit()
    row = db.execute("SELECT * FROM udalosti WHERE id=?", (uid,)).fetchone()
    return jsonify(ev_json(row))


@app.route("/api/udalosti/<int:uid>", methods=["DELETE"])
def delete_udalost(uid):
    db = get_db()
    db.execute("DELETE FROM udalosti WHERE id = ?", (uid,))
    db.commit()
    return jsonify({"ok": True})


# ── bulk import ────────────────────────────────────────────────────────────────

@app.route("/api/import", methods=["POST"])
def import_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Žiadne dáta"}), 400

    kol_list = data.get("kolegovia") or []
    zak_list = data.get("zakaznici") or []
    mer_list = data.get("meradla") or []
    ev_list  = data.get("events") or []

    db = get_db()
    db.execute("DELETE FROM udalosti")
    db.execute("DELETE FROM meradla")
    db.execute("DELETE FROM zakaznici")
    db.execute("DELETE FROM kolegovia")
    try:
        db.execute("DELETE FROM sqlite_sequence WHERE name IN "
                   "('udalosti','meradla','zakaznici','kolegovia')")
    except Exception:
        pass

    for k in kol_list:
        db.execute("INSERT INTO kolegovia (id, meno, farba) VALUES (?,?,?)",
                   (k.get("id"), k.get("meno", "?"), k.get("farba", "#2563EB")))

    for z in zak_list:
        db.execute("INSERT INTO zakaznici (id, nazov, ico) VALUES (?,?,?)",
                   (z.get("id"), z.get("nazov", "?"), z.get("ico")))

    for m in mer_list:
        db.execute("INSERT INTO meradla (id, nazov, inv) VALUES (?,?,?)",
                   (m.get("id"), m.get("nazov", "?"), m.get("inv")))

    for ev in ev_list:
        datum_do = ev.get("datumDo") or None
        db.execute(
            """INSERT INTO udalosti
               (id,typ,nazov,datum,datum_do,cas_od,cas_do,kolega_ids,zakaznik_id,
                meradla_ids,auto_znacka,auto_spz,dohlad_typ,miesto,popis)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                ev.get("id"),
                ev.get("typ") or "ine",
                ev.get("nazov"),
                ev.get("datum"),
                datum_do,
                ev.get("casOd"),
                ev.get("casDo"),
                json.dumps(ev.get("kolegaIds") or []),
                ev.get("zakaznikId"),
                json.dumps(ev.get("meradlaIds") or []),
                ev.get("autoZnacka"),
                ev.get("autoSpz"),
                ev.get("dohladTyp"),
                ev.get("miesto"),
                ev.get("popis"),
            ),
        )

    db.commit()
    return jsonify({"ok": True, "imported": len(ev_list)})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5050, debug=False)
