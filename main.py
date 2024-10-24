#!/usr/bin/env python3

import os
from datetime import datetime
from typing import List, Literal

from babel.dates import format_datetime
from cachelib.file import FileSystemCache
from flask import Flask, flash, redirect, render_template, request, session, url_for

from flask_session import Session
from models.drink import Drink
from models.user import User


# Configuration
class Config:
    SECRET_KEY = os.urandom(24)
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False  # Set according to your needs


app = Flask(__name__)
app.config.from_object(Config)

# Set up the session with CacheLib
app.config["SESSION_CACHE"] = FileSystemCache(
    "/tmp/flask_session",
    threshold=100,  # Maximum number of items to keep
    default_timeout=600,  # Adjust timeout as needed
)

# Use Flask-Session with CacheLib
Session(app)

# Constants
ALCOHOL_METABOLISM_RATE = 0.15  # Promille per hour
REDUCTION_FACTOR = {"male": 0.7, "female": 0.6}
ALCOHOL_ABSORPTION_RATE = 0.85
ETHANOL_DENSITY = 0.789  # g/mL

# Drink data
DRINKS = [
    Drink(name="Bier", volume=1000, unit="ml", alcohol=6),
    Drink(name="Bier", volume=0.5, alcohol=5),
    Drink(name="Bier", volume=0.33, alcohol=5),
    Drink(name="Rotwein", volume=0.2, alcohol=13),
    Drink(name="Weißwein", volume=0.2, alcohol=11),
    Drink(name="Sekt", volume=100, unit="ml", alcohol=11),
    Drink(name="Schnaps", volume=4, unit="cl", alcohol=40),
    Drink(name="Schnaps", volume=2, unit="cl", alcohol=40),
]


# Helper functions
def calculate_age_factor(age: int) -> float:
    return 1 - ((age - 20) * 0.001) if age > 20 else 1


def calculate_reduction_factor(gender: Literal["male", "female"], age: int) -> float:
    age_factor = calculate_age_factor(age)
    return REDUCTION_FACTOR.get(gender, 1) * age_factor


def calculate_bac(
    weight: float, gender: Literal["male", "female"], age: int, total_alcohol: float
) -> float:
    reduction_factor = calculate_reduction_factor(gender, age)
    absorbed_alcohol = total_alcohol * 1000 * ALCOHOL_ABSORPTION_RATE
    return round(absorbed_alcohol / (weight * reduction_factor), 3)


def calculate_adjusted_metabolism_rate(age: int, weight: float) -> float:
    age_adjustment = 1 - ((age - 20) * 0.001)
    metabolism_rate = ALCOHOL_METABOLISM_RATE * age_adjustment
    metabolism_rate = max(0.10, metabolism_rate)  # Lower bound
    weight_factor = weight / 70  # Baseline weight
    return metabolism_rate * weight_factor


def calculate_time_to_sober(bac: float, weight: float, age: int) -> float:
    final_metabolism_rate = calculate_adjusted_metabolism_rate(age, weight)
    return round(bac / final_metabolism_rate, 2)


def calculate_total_alcohol_in_liters(drinks: List[Drink]) -> float:
    result = round(sum(drink.alcohol_content() for drink in drinks), 2)
    return result


def get_combined_drinks() -> List[Drink]:
    user_drinks = [Drink(**drink) for drink in session.get("user_drinks", [])]
    custom_drinks = [Drink(**drink) for drink in session.get("custom_drinks", [])]
    combined_drinks = user_drinks + custom_drinks

    # sort the drinks by highest alcohol content
    combined_drinks.sort(key=lambda x: x.volume_in_liters(), reverse=True)

    return combined_drinks


@app.route("/")
def index():
    selected_drinks = get_combined_drinks()
    drink_summary = {
        f"{drink.__str__()}": selected_drinks.count(drink) for drink in selected_drinks
    }
    context = {
        "drinks": DRINKS,
        "drink_summary": drink_summary,
        "selected_drinks": get_combined_drinks(),
        "user": session.get("user"),
        "current_year": datetime.now().year,
    }
    return render_template("index.html", **context)


@app.route("/history")
def history():
    drink_history = session.get("history", [])
    context = {
        "drink_history": drink_history,
    }
    return render_template("history.html", **context)


@app.route("/history/reset")
def reset_history():
    session["history"] = []
    session["user_drinks"] = []
    session["custom_drinks"] = []
    session.modified = True
    flash("History reset.")
    return redirect(url_for("history"))


@app.route("/history/remove", methods=["POST"])
def remove_history_entry():
    drink = request.form.get("drink")
    time = request.form.get("time")
    history = session.get("history", [])
    for entry in history:
        if entry["drink"] == drink and entry["time"] == time:
            history.remove(entry)
            break
    session["history"] = history
    session.modified = True
    flash("History entry removed.")
    return redirect(url_for("history"))


@app.route("/add_drink", methods=["POST"])
def add_drink():
    drink = request.form.get("drink")
    selected_drink = next((d for d in DRINKS if d.__str__() == drink), None)

    if not selected_drink:
        flash("Drink not found.")
        return redirect(url_for("index"))

    user_drinks = session.setdefault("user_drinks", [])
    user_drinks.append(selected_drink.__dict__)

    log = {
        "drink": selected_drink.__str__(),
        "time": format_datetime(datetime.now(), locale="de_DE"),
        "timestamp": datetime.now().timestamp(),
    }
    history = session.get("history", [])
    history.append(log)
    session["history"] = history
    session.modified = True
    flash(f"{selected_drink.name} added.")
    return redirect(url_for("index"))


@app.route("/remove_drink", methods=["POST"])
def remove_drink():
    drink = request.form.get("drink")
    selected_drink = next((d for d in DRINKS if d.__str__() == drink), None)

    if not selected_drink:
        flash("Drink not found.")
        return redirect(url_for("index"))

    user_drinks = session.get("user_drinks", [])
    user_drinks.remove(selected_drink.__dict__)

    # Update history
    history = session.get("history", [])
    for entry in history:
        if entry["drink"] == selected_drink.__str__():
            history.remove(entry)
            break
    session["history"] = history

    session.modified = True
    flash(f"{selected_drink.name} removed.")
    return redirect(url_for("index") + "#drinks")


@app.route("/add_custom_drink", methods=["POST"])
def add_custom_drink():
    try:
        custom_drink = Drink(
            name=request.form["custom-drink-name"],
            alcohol=float(request.form["custom-drink-alcohol"]),
            volume=float(request.form["custom-drink-volume"]),
            unit=request.form.get("custom-drink-unit", "ml"),
        )
        custom_drinks = session.setdefault("custom_drinks", [])
        custom_drinks.append(custom_drink.__dict__)
        session.modified = True
        flash(f"Custom drink {custom_drink.name} added.")
    except ValueError:
        flash("Invalid input. Please enter numbers for volume and alcohol content.")
    return redirect(url_for("index"))


@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        weight = float(request.form.get("weight", 70))
        gender = request.form.get("gender", "male")
        age = int(request.form.get("age", 20))

        user = User(
            name="User",
            weight=weight,
            gender=gender,
            age=age,
        )
        session["user"] = user.__dict__
        session.modified = True
    except (ValueError, KeyError):
        return render_template(
            "result.html",
            error="Ungültige Eingaben. Bitte überprüfen Sie die eingegebenen Informationen.",
            drinks=[],
        )

    selected_drinks = get_combined_drinks()

    if not selected_drinks:
        return render_template(
            "result.html", error="Keine Getränke ausgewählt.", drinks=[]
        )

    try:
        total_alcohol = calculate_total_alcohol_in_liters(selected_drinks)
        bac = calculate_bac(
            weight=user.weight,
            gender=user.gender,
            age=user.age,
            total_alcohol=total_alcohol,
        )
        time_to_sober = calculate_time_to_sober(
            bac=bac, weight=user.weight, age=user.age
        )
    except Exception as e:
        print(e)
        return render_template(
            "result.html",
            error="Fehler bei der Berechnung. Bitte versuchen Sie es erneut.",
            drinks=[],
        )

    drink_summary = {
        f"{drink}": selected_drinks.count(drink) for drink in selected_drinks
    }

    return render_template(
        "result.html", time=time_to_sober, bac=bac, drinks=drink_summary
    )


@app.route("/reset")
def reset():
    # session.clear()
    session["user_drinks"] = []
    session["custom_drinks"] = []
    session["history"] = []
    flash("Session reset.")
    return redirect(url_for("index"))


@app.route("/health-check")
def health_check():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
