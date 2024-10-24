#!/usr/bin/env python3

import os
from datetime import datetime
from typing import List, Literal

from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from flask_session import Session
from models.drink import Drink
from models.user import User

app = Flask(__name__)


# Configuration
class Config:
    SECRET_KEY = os.urandom(24)
    SESSION_TYPE = "filesystem"


app = Flask(__name__)
app.config.from_object(Config)

Session(app)

ALCOHOL_METABOLISM_RATE = 0.15  # Promille per hour
REDUCTION_FACTOR = {"male": 0.7, "female": 0.6}
ALCOHOL_ABSORPTION_RATE = 0.85

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
def calculate_bac(
    weight: float, gender: Literal["male", "female"], age: int, total_alcohol: float
) -> float:
    # Adjust the reduction factor based on age if necessary
    age_factor = 1 - ((age - 20) * 0.001) if age > 20 else 1
    reduction_factor = REDUCTION_FACTOR.get(gender, 1) * age_factor
    absorbed_alcohol = total_alcohol * ALCOHOL_ABSORPTION_RATE
    return round(absorbed_alcohol / (weight * reduction_factor), 3)


def calculate_time_to_sober(bac: float, weight: float, age: int) -> float:
    # Adjust metabolism rate based on age and weight
    adjusted_metabolism_rate = ALCOHOL_METABOLISM_RATE * (1 - ((age - 20) * 0.001))
    adjusted_metabolism_rate = max(0.10, adjusted_metabolism_rate)  # Set a lower bound

    weight_factor = weight / 70  # Assume 70 kg as baseline
    final_metabolism_rate = adjusted_metabolism_rate * weight_factor
    return round(bac / final_metabolism_rate, 2)


def calculate_total_alcohol(selected_drinks: List[Drink]) -> float:
    return sum(
        drink.volume_in_liters() * drink.alcohol * 0.789 for drink in selected_drinks
    )


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


@app.route("/add_drink", methods=["POST"])
def add_drink():
    drink = request.form.get("drink")
    selected_drink = next((d for d in DRINKS if d.__str__() == drink), None)

    if not selected_drink:
        flash("Drink not found.")
        return redirect(url_for("index"))

    user_drinks = session.setdefault("user_drinks", [])
    user_drinks.append(selected_drink.__dict__)
    session.modified = True
    flash(f"{selected_drink.name} added.")
    return redirect(url_for("index") + "#drinks")


@app.route("/remove_drink", methods=["POST"])
def remove_drink():
    drink = request.form.get("drink")
    selected_drink = next((d for d in DRINKS if d.__str__() == drink), None)

    if not selected_drink:
        flash("Drink not found.")
        return redirect(url_for("index"))

    user_drinks = session.get("user_drinks", [])
    user_drinks.remove(selected_drink.__dict__)
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
        # Attempt to create a User object with defaults for missing values
        weight = float(request.form.get("weight", 70))
        gender = request.form.get("gender", "male")
        age = int(request.form.get("age", 20))

        user = User(
            name="User",  # Name can be static or from session
            weight=weight,
            gender=gender,
            age=age,
        )
        session["user"] = user.__dict__
        session.modified = True
    except (ValueError, KeyError) as e:
        # Render template with an error message if inputs are invalid
        return render_template(
            "result.html",
            error="Ungültige Eingaben. Bitte überprüfen Sie die eingegebenen Informationen.",
            drinks=[],
        )

    # Retrieve selected drinks
    selected_drinks = get_combined_drinks()

    # Handle the case where no drinks are selected
    if not selected_drinks:
        return render_template(
            "result.html", error="Keine Getränke ausgewählt.", drinks=[]
        )

    # Calculate total alcohol and BAC
    try:
        total_alcohol = calculate_total_alcohol(selected_drinks)
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
        # Catch any unexpected errors during calculation
        print(e)
        return render_template(
            "result.html",
            error="Fehler bei der Berechnung. Bitte versuchen Sie es erneut.",
            drinks=[],
        )

    # Summarize the drinks for display
    drink_summary = {
        f"{drink}": selected_drinks.count(drink) for drink in selected_drinks
    }

    # Render the result page with calculated values
    return render_template(
        "result.html", time=time_to_sober, bac=bac, drinks=drink_summary
    )


@app.route("/reset")
def reset():
    # session.clear()
    session["user_drinks"] = []
    session["custom_drinks"] = []
    flash("Session reset.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
