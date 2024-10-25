#!/usr/bin/env python3

import logging
import os
from datetime import datetime
from typing import List, Literal

from babel.dates import format_datetime
from cachelib.file import FileSystemCache
from flask import Flask, flash, redirect, render_template, request, session, url_for

from flask_session import Session
from models.drink import Drink
from models.user import User

app = Flask(__name__)


# Configuration
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(24))
    SESSION_PERMANENT = False
    SESSION_COOKIE_NAME = "session"
    SESSION_TYPE = "filesystem"


app.config.from_object(Config)

# Initialize cache
cache = FileSystemCache(
    cache_dir="/tmp/flask_session",
    threshold=250,
    default_timeout=60 * 60 * 24 * 7,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format='"%(asctime)s" "%(levelname)s" - "%(message)s"'
)
logger = logging.getLogger(__name__)

# Initialize Flask-Session
Session(app)

# Constants
ALCOHOL_METABOLISM_RATE = 0.15
REDUCTION_FACTOR = {"male": 0.7, "female": 0.6}
ALCOHOL_ABSORPTION_RATE = 0.85
ETHANOL_DENSITY = 0.789

# Drink data
DRINKS = [
    Drink(name="Bier", volume=1.0, unit="L", alcohol=6),
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
    return round(1 - ((age - 20) * 0.001) if age > 20 else 1, 2)


def calculate_reduction_factor(gender: Literal["male", "female"], age: int) -> float:
    return REDUCTION_FACTOR.get(gender, 0.7) * calculate_age_factor(age)


def calculate_bac(
    weight: float, gender: Literal["male", "female"], age: int, total_alcohol: float
) -> float:
    reduction_factor = calculate_reduction_factor(gender, age)
    absorbed_alcohol = round(total_alcohol * ALCOHOL_ABSORPTION_RATE, 2)
    return round(absorbed_alcohol / (weight * reduction_factor), 3)


def calculate_adjusted_metabolism_rate(age: int, weight: float) -> float:
    metabolism_rate = ALCOHOL_METABOLISM_RATE * calculate_age_factor(age)
    metabolism_rate = max(0.10, metabolism_rate)
    weight_factor = weight / 70
    return round(metabolism_rate * weight_factor, 2)


def calculate_time_to_sober(bac: float, weight: float, age: int) -> float:
    final_metabolism_rate = calculate_adjusted_metabolism_rate(age, weight)
    time_to_sober = round(bac / final_metabolism_rate, 2)
    logger.info(f"With values age={age} weigth={weight} bac={bac}")
    logger.info(f"Final metabolism rate: {final_metabolism_rate}")
    logger.info(f"Time to sober: {time_to_sober} hours")

    return time_to_sober


def calculate_total_alcohol_in_grams(drinks: List[Drink]) -> float:
    return round(sum(drink.alcohol_grams() for drink in drinks), 2)


def get_combined_drinks() -> List[Drink]:
    user_drinks = [Drink(**drink) for drink in session.get("user_drinks", [])]
    custom_drinks = [Drink(**drink) for drink in session.get("custom_drinks", [])]
    combined_drinks = user_drinks + custom_drinks
    combined_drinks.sort(key=lambda x: x.volume_in_liters(), reverse=True)
    return combined_drinks


# Routes
@app.route("/")
def index():
    # Get combined selected drinks
    selected_drinks = get_combined_drinks()

    # Generate a summary of selected drinks
    drink_summary = {
        f"{drink}": selected_drinks.count(drink) for drink in selected_drinks
    }

    # Combine selected drinks with predefined DRINKS
    all_unique_drinks = set(selected_drinks).union(DRINKS)

    # Sort the drinks by volume in liters in descending order
    drinks = sorted(all_unique_drinks, key=lambda x: x.volume_in_liters(), reverse=True)

    # Create context for rendering the template
    context = {
        "drinks": drinks,
        "drink_summary": drink_summary,
        "selected_drinks": selected_drinks,
        "user": session.get("user"),
        "current_year": datetime.now().year,
    }

    # Render the template with the context
    return render_template("index.html", **context)


@app.route("/history")
def history():
    return render_template("history.html", drink_history=session.get("history", []))


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
    session["history"] = [
        entry for entry in history if entry["drink"] != drink or entry["time"] != time
    ]
    session.modified = True
    flash("History entry removed.")
    return redirect(url_for("history"))


@app.route("/add_drink", methods=["POST"])
def add_drink():
    drink = request.form.get("drink")
    all_unique_drinks = set(get_combined_drinks() + DRINKS)

    selected_drink = next((d for d in all_unique_drinks if str(d) == drink), None)

    if not selected_drink:
        flash("Drink not found.")
        return redirect(url_for("index"))

    user_drinks = session.setdefault("user_drinks", [])
    user_drinks.append(selected_drink.__dict__)

    log = {
        "drink": str(selected_drink),
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
    all_unique_drinks = set(get_combined_drinks() + DRINKS)
    selected_drink = next((d for d in all_unique_drinks if str(d) == drink), None)

    if not selected_drink:
        flash("Drink not found.")
        return redirect(url_for("index"))

    user_drinks = session.get("user_drinks", [])
    user_drinks.remove(selected_drink.__dict__)

    history = session.get("history", [])
    session["history"] = [
        entry for entry in history if entry["drink"] != str(selected_drink)
    ]
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

        log = {
            "drink": str(custom_drink),
            "time": format_datetime(datetime.now(), locale="de_DE"),
            "timestamp": datetime.now().timestamp(),
        }
        history = session.get("history", [])
        history.append(log)
        session["history"] = history

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
            "result.html", error="Invalid input. Please check your details.", drinks=[]
        )

    selected_drinks = get_combined_drinks()

    if not selected_drinks:
        return render_template("result.html", error="No drinks selected.", drinks=[])

    try:
        total_alcohol = calculate_total_alcohol_in_grams(selected_drinks)
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
        logger.error(e)
        return render_template(
            "result.html", error="Calculation error. Please try again.", drinks=[]
        )

    drink_summary = {
        str(drink): selected_drinks.count(drink) for drink in selected_drinks
    }

    return render_template(
        "result.html", time=time_to_sober, bac=bac, drinks=drink_summary
    )


@app.route("/reset")
def reset():
    session.clear()
    session["user_drinks"] = []
    session["custom_drinks"] = []
    session["history"] = []
    flash("Session reset.")
    return redirect(url_for("index"))


@app.route("/health-check")
def health_check():
    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
