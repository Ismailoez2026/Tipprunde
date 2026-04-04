from datetime import datetime
import csv
import io
import os

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint


app = Flask(__name__)
database_url = os.getenv("DATABASE_URL", "sqlite:///tipprunde.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

ADMIN_CODE = os.getenv("ADMIN_CODE", "admin123")


FLAG_MAP = {
    "argentinien": "🇦🇷",
    "argentina": "🇦🇷",
    "australien": "🇦🇺",
    "australia": "🇦🇺",
    "belgien": "🇧🇪",
    "belgium": "🇧🇪",
    "bolivien": "🇧🇴",
    "bolivia": "🇧🇴",
    "brasilien": "🇧🇷",
    "brazil": "🇧🇷",
    "kanada": "🇨🇦",
    "canada": "🇨🇦",
    "chile": "🇨🇱",
    "kolumbien": "🇨🇴",
    "colombia": "🇨🇴",
    "kroatien": "🇭🇷",
    "croatia": "🇭🇷",
    "tschechien": "🇨🇿",
    "czech republic": "🇨🇿",
    "dänemark": "🇩🇰",
    "daenemark": "🇩🇰",
    "denmark": "🇩🇰",
    "ecuador": "🇪🇨",
    "england": "🏴",
    "frankreich": "🇫🇷",
    "france": "🇫🇷",
    "deutschland": "🇩🇪",
    "germany": "🇩🇪",
    "ghana": "🇬🇭",
    "griechenland": "🇬🇷",
    "greece": "🇬🇷",
    "iran": "🇮🇷",
    "irland": "🇮🇪",
    "ireland": "🇮🇪",
    "italien": "🇮🇹",
    "italy": "🇮🇹",
    "japan": "🇯🇵",
    "mexiko": "🇲🇽",
    "mexico": "🇲🇽",
    "marokko": "🇲🇦",
    "morocco": "🇲🇦",
    "niederlande": "🇳🇱",
    "netherlands": "🇳🇱",
    "neuseeland": "🇳🇿",
    "new zealand": "🇳🇿",
    "nigeria": "🇳🇬",
    "norwegen": "🇳🇴",
    "norway": "🇳🇴",
    "paraguay": "🇵🇾",
    "peru": "🇵🇪",
    "polen": "🇵🇱",
    "poland": "🇵🇱",
    "portugal": "🇵🇹",
    "katar": "🇶🇦",
    "qatar": "🇶🇦",
    "rumänien": "🇷🇴",
    "rumaenien": "🇷🇴",
    "romania": "🇷🇴",
    "saudi-arabien": "🇸🇦",
    "saudi arabia": "🇸🇦",
    "senegal": "🇸🇳",
    "serbien": "🇷🇸",
    "serbia": "🇷🇸",
    "südkorea": "🇰🇷",
    "suedkorea": "🇰🇷",
    "south korea": "🇰🇷",
    "spanien": "🇪🇸",
    "spain": "🇪🇸",
    "schweiz": "🇨🇭",
    "switzerland": "🇨🇭",
    "tunesien": "🇹🇳",
    "tunisia": "🇹🇳",
    "türkei": "🇹🇷",
    "tuerkei": "🇹🇷",
    "turkey": "🇹🇷",
    "ukraine": "🇺🇦",
    "uruguay": "🇺🇾",
    "usa": "🇺🇸",
    "vereinigte staaten": "🇺🇸",
    "united states": "🇺🇸",
    "wales": "🏴",
    "kamerun": "🇨🇲",
    "cameroon": "🇨🇲",
    "costa rica": "🇨🇷",
    "ägypten": "🇪🇬",
    "aegypten": "🇪🇬",
    "egypt": "🇪🇬",
    "österreich": "🇦🇹",
    "oesterreich": "🇦🇹",
    "austria": "🇦🇹",
    "südafrika": "🇿🇦",
    "suedafrika": "🇿🇦",
    "south africa": "🇿🇦",
    "algerien": "🇩🇿",
    "algeria": "🇩🇿",
    "island": "🇮🇸",
    "iceland": "🇮🇸",
    "schottland": "🏴",
    "scotland": "🏴",
}

def get_flag(team_name: str) -> str:
    if not team_name:
        return "🏳️"
    return FLAG_MAP.get(team_name.strip().lower(), "🏳️")


def result_text(match):
    if match.has_result():
        return f"{match.result_home}:{match.result_away}"
    return "-:-"


@app.context_processor
def inject_globals():
    return {
        "get_flag": get_flag,
        "result_text": result_text,
    }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    home_team = db.Column(db.String(80), nullable=False)
    away_team = db.Column(db.String(80), nullable=False)
    kickoff = db.Column(db.DateTime, nullable=False)
    stage = db.Column(db.String(50), nullable=False, default="Gruppenphase")
    group_name = db.Column(db.String(20), nullable=True)
    result_home = db.Column(db.Integer, nullable=True)
    result_away = db.Column(db.Integer, nullable=True)

    def has_started(self):
        return datetime.now() >= self.kickoff

    def has_result(self):
        return self.result_home is not None and self.result_away is not None


class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey("match.id"), nullable=False)
    pred_home = db.Column(db.Integer, nullable=False)
    pred_away = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    user = db.relationship("User", backref="predictions")
    match = db.relationship("Match", backref="predictions")

    __table_args__ = (
        UniqueConstraint("user_id", "match_id", name="uq_user_match_prediction"),
    )


class BonusPrediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    champion_team = db.Column(db.String(80), nullable=False)
    user = db.relationship("User", backref="bonus_prediction")


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    champion_result = db.Column(db.String(80), nullable=True)
    rules_text = db.Column(db.Text, nullable=True)


DEFAULT_RULES = """
1. Tipps können bis zum Anstoß eines Spiels abgegeben oder geändert werden. Ab Anstoß ist der Tipp gesperrt.
2. 4 Punkte für das exakte Ergebnis.
3. 3 Punkte für die richtige Tordifferenz.
4. 2 Punkte für die richtige Tendenz (richtiger Sieger oder richtiges Unentschieden).
5. Vor Anstoß sind die Tipps anderer Teilnehmer nicht sichtbar. Ab Anstoß sind alle Tipps sichtbar.
6. Gewertet wird nur das Ergebnis nach regulärer Spielzeit inklusive Nachspielzeit. Verlängerung und Elfmeterschießen zählen nicht.
7. Vor dem ersten WM-Spiel kann jeder einen Weltmeistertipp abgeben. Richtiger Tipp = 10 Zusatzpunkte.
""".strip()


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)


def is_admin():
    return session.get("is_admin", False)


def get_or_create_settings():
    settings = Settings.query.first()
    if not settings:
        settings = Settings(rules_text=DEFAULT_RULES)
        db.session.add(settings)
        db.session.commit()
    elif not settings.rules_text:
        settings.rules_text = DEFAULT_RULES
        db.session.commit()
    return settings


def get_first_kickoff():
    first_match = Match.query.order_by(Match.kickoff.asc()).first()
    return first_match.kickoff if first_match else None


def bonus_is_open():
    first_kickoff = get_first_kickoff()
    if not first_kickoff:
        return True
    return datetime.now() < first_kickoff


def match_is_open(match: Match):
    return datetime.now() < match.kickoff


def visible_predictions(match: Match):
    if match.has_started():
        return Prediction.query.filter_by(match_id=match.id).order_by(Prediction.created_at.asc()).all()

    current_user = get_current_user()
    if not current_user:
        return []

    return Prediction.query.filter_by(match_id=match.id, user_id=current_user.id).all()


def tendency(a, b):
    if a > b:
        return 1
    if a < b:
        return -1
    return 0


def calculate_points(pred_home, pred_away, res_home, res_away):
    if pred_home == res_home and pred_away == res_away:
        return 4
    if (pred_home - pred_away) == (res_home - res_away):
        return 3
    if tendency(pred_home, pred_away) == tendency(res_home, res_away):
        return 2
    return 0


def user_total_points(user: User):
    total = 0
    for pred in user.predictions:
        match = pred.match
        if match.has_result():
            total += calculate_points(pred.pred_home, pred.pred_away, match.result_home, match.result_away)

    settings = get_or_create_settings()
    bonus = BonusPrediction.query.filter_by(user_id=user.id).first()
    if bonus and settings.champion_result:
        if bonus.champion_team.strip().lower() == settings.champion_result.strip().lower():
            total += 10
    return total


def ranking():
    users = User.query.order_by(User.name.asc()).all()
    rows = []
    for user in users:
        exact = 0
        diff = 0
        tendency_count = 0
        for pred in user.predictions:
            match = pred.match
            if not match.has_result():
                continue
            pts = calculate_points(pred.pred_home, pred.pred_away, match.result_home, match.result_away)
            if pts == 4:
                exact += 1
            elif pts == 3:
                diff += 1
            elif pts == 2:
                tendency_count += 1

        rows.append({
            "user": user,
            "total": user_total_points(user),
            "exact_count": exact,
            "diff_count": diff,
            "tendency_count": tendency_count
        })

    rows.sort(key=lambda x: (-x["total"], -x["exact_count"], -x["diff_count"], -x["tendency_count"], x["user"].name.lower()))
    return rows


@app.route("/")
def index():
    current_user = get_current_user()
    matches = Match.query.order_by(Match.kickoff.asc()).all()
    user_predictions = {}

    if current_user:
        preds = Prediction.query.filter_by(user_id=current_user.id).all()
        user_predictions = {p.match_id: p for p in preds}

    rows = [{
        "match": match,
        "display_predictions": visible_predictions(match),
        "open": match_is_open(match),
    } for match in matches]

    bonus_prediction = None
    if current_user:
        bonus_prediction = BonusPrediction.query.filter_by(user_id=current_user.id).first()

    settings = get_or_create_settings()

    return render_template(
        "index.html",
        current_user=current_user,
        rows=rows,
        user_predictions=user_predictions,
        ranking_rows=ranking(),
        bonus_prediction=bonus_prediction,
        bonus_open=bonus_is_open(),
        champion_result=settings.champion_result,
        rules_text=settings.rules_text,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Bitte einen Namen eingeben.")
            return redirect(url_for("login"))

        user = User.query.filter_by(name=name).first()
        if not user:
            user = User(name=name)
            db.session.add(user)
            db.session.commit()

        session["user_id"] = user.id
        flash(f"Angemeldet als {user.name}.")
        return redirect(url_for("index"))

    return render_template("login.html", current_user=get_current_user())


@app.route("/logout")
def logout():
    session.clear()
    flash("Du wurdest abgemeldet.")
    return redirect(url_for("index"))


@app.route("/tip/<int:match_id>", methods=["POST"])
def save_tip(match_id):
    current_user = get_current_user()
    if not current_user:
        flash("Bitte zuerst anmelden.")
        return redirect(url_for("login"))

    match = db.session.get(Match, match_id)
    if not match:
        flash("Spiel nicht gefunden.")
        return redirect(url_for("index"))

    if not match_is_open(match):
        flash("Tipp ist ab Anstoß gesperrt.")
        return redirect(url_for("index"))

    try:
        pred_home = int(request.form.get("pred_home", "").strip())
        pred_away = int(request.form.get("pred_away", "").strip())
        if pred_home < 0 or pred_away < 0:
            raise ValueError
    except ValueError:
        flash("Bitte gültige Tore eingeben.")
        return redirect(url_for("index"))

    existing = Prediction.query.filter_by(user_id=current_user.id, match_id=match.id).first()
    if existing:
        existing.pred_home = pred_home
        existing.pred_away = pred_away
        existing.created_at = datetime.now()
        flash(f"Tipp für {match.home_team} - {match.away_team} aktualisiert.")
    else:
        db.session.add(Prediction(user_id=current_user.id, match_id=match.id, pred_home=pred_home, pred_away=pred_away))
        flash(f"Tipp für {match.home_team} - {match.away_team} gespeichert.")

    db.session.commit()
    return redirect(url_for("index"))


@app.route("/bonus", methods=["POST"])
def save_bonus():
    current_user = get_current_user()
    if not current_user:
        flash("Bitte zuerst anmelden.")
        return redirect(url_for("login"))

    if not bonus_is_open():
        flash("Der Weltmeister-Bonustipp ist bereits gesperrt.")
        return redirect(url_for("index"))

    champion_team = request.form.get("champion_team", "").strip()
    if not champion_team:
        flash("Bitte ein Team für den Weltmeistertipp eingeben.")
        return redirect(url_for("index"))

    existing = BonusPrediction.query.filter_by(user_id=current_user.id).first()
    if existing:
        existing.champion_team = champion_team
        flash("Weltmeistertipp aktualisiert.")
    else:
        db.session.add(BonusPrediction(user_id=current_user.id, champion_team=champion_team))
        flash("Weltmeistertipp gespeichert.")

    db.session.commit()
    return redirect(url_for("index"))


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("code", "") == ADMIN_CODE:
            session["is_admin"] = True
            flash("Admin-Modus aktiviert.")
            return redirect(url_for("admin"))
        flash("Falscher Admin-Code.")
        return redirect(url_for("admin_login"))

    return render_template("admin_login.html", current_user=get_current_user())


@app.route("/admin")
def admin():
    if not is_admin():
        return redirect(url_for("admin_login"))

    return render_template(
        "admin.html",
        matches=Match.query.order_by(Match.kickoff.asc()).all(),
        settings=get_or_create_settings(),
        current_user=get_current_user()
    )


@app.route("/admin/add-match", methods=["POST"])
def add_match():
    if not is_admin():
        return redirect(url_for("admin_login"))

    home_team = request.form.get("home_team", "").strip()
    away_team = request.form.get("away_team", "").strip()
    kickoff_str = request.form.get("kickoff", "").strip()
    stage = request.form.get("stage", "Gruppenphase").strip() or "Gruppenphase"
    group_name = request.form.get("group_name", "").strip() or None

    if not home_team or not away_team or not kickoff_str:
        flash("Bitte alle Felder ausfüllen.")
        return redirect(url_for("admin"))

    try:
        kickoff = datetime.strptime(kickoff_str, "%Y-%m-%dT%H:%M")
    except ValueError:
        flash("Ungültiges Datum/Zeit-Format.")
        return redirect(url_for("admin"))

    db.session.add(Match(home_team=home_team, away_team=away_team, kickoff=kickoff, stage=stage, group_name=group_name))
    db.session.commit()
    flash("Spiel hinzugefügt.")
    return redirect(url_for("admin"))


@app.route("/admin/import-csv", methods=["POST"])
def import_csv():
    if not is_admin():
        return redirect(url_for("admin_login"))

    file = request.files.get("csv_file")
    if not file or not file.filename:
        flash("Bitte eine CSV-Datei auswählen.")
        return redirect(url_for("admin"))

    try:
        content = file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        required_fields = {"home_team", "away_team", "kickoff"}
        if not required_fields.issubset(set(reader.fieldnames or [])):
            flash("CSV braucht mindestens die Spalten: home_team, away_team, kickoff")
            return redirect(url_for("admin"))

        count = 0
        for row in reader:
            home_team = (row.get("home_team") or "").strip()
            away_team = (row.get("away_team") or "").strip()
            kickoff_str = (row.get("kickoff") or "").strip()
            stage = (row.get("stage") or "Gruppenphase").strip() or "Gruppenphase"
            group_name = (row.get("group_name") or "").strip() or None

            if not home_team or not away_team or not kickoff_str:
                continue

            kickoff = datetime.strptime(kickoff_str, "%Y-%m-%d %H:%M")
            exists = Match.query.filter_by(home_team=home_team, away_team=away_team, kickoff=kickoff).first()
            if exists:
                continue

            db.session.add(Match(home_team=home_team, away_team=away_team, kickoff=kickoff, stage=stage, group_name=group_name))
            count += 1

        db.session.commit()
        flash(f"{count} Spiele importiert.")
    except Exception as exc:
        flash(f"CSV-Import fehlgeschlagen: {exc}")

    return redirect(url_for("admin"))


@app.route("/admin/result/<int:match_id>", methods=["POST"])
def save_result(match_id):
    if not is_admin():
        return redirect(url_for("admin_login"))

    match = db.session.get(Match, match_id)
    if not match:
        flash("Spiel nicht gefunden.")
        return redirect(url_for("admin"))

    try:
        result_home = int(request.form.get("result_home", "").strip())
        result_away = int(request.form.get("result_away", "").strip())
        if result_home < 0 or result_away < 0:
            raise ValueError
    except ValueError:
        flash("Bitte gültige Tore eintragen.")
        return redirect(url_for("admin"))

    match.result_home = result_home
    match.result_away = result_away
    db.session.commit()
    flash(f"Ergebnis für {match.home_team} - {match.away_team} gespeichert.")
    return redirect(url_for("admin"))


@app.route("/admin/champion", methods=["POST"])
def save_champion_result():
    if not is_admin():
        return redirect(url_for("admin_login"))

    settings = get_or_create_settings()
    champion_result = request.form.get("champion_result", "").strip()
    settings.champion_result = champion_result if champion_result else None
    db.session.commit()
    flash("Weltmeister-Ergebnis gespeichert.")
    return redirect(url_for("admin"))


@app.route("/admin/rules", methods=["POST"])
def save_rules():
    if not is_admin():
        return redirect(url_for("admin_login"))

    settings = get_or_create_settings()
    rules_text = request.form.get("rules_text", "").strip()
    settings.rules_text = rules_text or DEFAULT_RULES
    db.session.commit()
    flash("Regeln gespeichert.")
    return redirect(url_for("admin"))


@app.route("/init-db")
def init_db():
    db.create_all()
    get_or_create_settings()

    if Match.query.count() == 0:
        db.session.add_all([
            Match(home_team="Deutschland", away_team="Frankreich", kickoff=datetime(2026, 6, 12, 21, 0), stage="Gruppenphase", group_name="A"),
            Match(home_team="Brasilien", away_team="Spanien", kickoff=datetime(2026, 6, 13, 18, 0), stage="Gruppenphase", group_name="B"),
            Match(home_team="Argentinien", away_team="Portugal", kickoff=datetime(2026, 6, 14, 20, 0), stage="Gruppenphase", group_name="C"),
        ])
        db.session.commit()

    return "Datenbank initialisiert."


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        get_or_create_settings()

    app.run(debug=True, host="0.0.0.0", port=5001)
