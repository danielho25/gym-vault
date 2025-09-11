import lmstudio as lms
import json
import time
from typing import Dict, Any, List
from collections import defaultdict
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import datetime
from openai import OpenAI
from openai_harmony import (
    Author,
    Conversation,
    DeveloperContent,
    HarmonyEncodingName,
    Message,
    Role,
    SystemContent,
    ToolDescription,
    load_harmony_encoding,
    ReasoningEffort,
)

"""
in this program we will be creating the tools for gpt-oss to use when users submit a new workout 
from the form provided in the frontend. there will be a notes section to ask any follow up questions.
the program will analyze the notes section and use tools based on this.
The tools will be: 

analyze (analyzes workouts for how many sets, reps, weight, time taken, muscles targeted. calculates intensity level)
meal_recommender (recommends a healthy meal with macros)
plan_recovery (takes intensity levels and nutrition, recommends next time to train, sleep levels, hydration, 
workout frequency, injury patterns, fatigue, etc)


the main functions called after every submitted workout will be:

store_workout (adds workout to sqlite)
graph_workout (adds workout data to a progress graph) 
and ask_coach_mike (act as a fitness coach mike and provide chatbot assistance)
"""

# MAIN FUNCTIONS

# ------- store data in sqlite ---------
create_workout_table = """
CREATE TABLE IF NOT EXISTS workout (
    workout_id SERIAL PRIMARY KEY,   -- unique ID
    workout_date DATE NOT NULL,
    workout_time TIME NOT NULL
);
"""

create_exercise_table = """
CREATE TABLE IF NOT EXISTS workout_exercise (
    exercise_id SERIAL PRIMARY KEY,
    workout_id INT NOT NULL,
    exercise_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (workout_id) REFERENCES workout(workout_id) ON DELETE CASCADE
);
"""

database = 'workout_data.db'


def create_table():
    try:
        with sqlite3.connect(database) as conn:
            cursor = conn.cursor()
            cursor.execute(create_workout_table)
            cursor.execute(create_exercise_table)
            conn.commit()
            print("Workout stored successfully!")
            return True
    except sqlite3.OperationalError as e:
        print(f"Error creating tables: {e}")
        conn.rollback()
        return False
    except Exception as e:
        print(f"Unexpected Error Occurred: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def store_workout():
    try:
        with sqlite3.connect(database) as conn:
            cursor = conn.cursor()

            # insert to workout table
            cursor.execute("""
            INSERT INTO workout (workout_date, workout_time)
            VALUES (?, ?)
            """, ("2025-09-10", "07:30"))

            # insert to exercise table
            workout_id = cursor.lastrowid  # get the last row id to match the tables

            # sample exercises to add, get from form later
            exercises = ["squat", "bench", "deadlift"]
            for ex in exercises:
                cursor.execute("""
                INSERT INTO workout_exercise (workout_id, exercise_name)
                VALUES (?, ?)""", (workout_id, ex))
            conn.commit()
            print("Workout stored successfully!")
            return True
    except sqlite3.OperationalError as e:
        print(f"Insertion failed: {e}")
        conn.rollback()
        return False
    except Exception as e:
        print(f"Unexpected Error Occurred: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


# ----- graph workout --------
# example stored workout data using default dict structure defaultdict(tuple[sets, reps, weight])

def graph_workout(workout_entry, exercise_entry):
    """
    if no graph, creates a new graph. if graph already exists, add a new plot
    :return: new graph or new plot on graph
    """
    workout_data = []
    exercise_data = []

    workout_id = "workout_tracker"

    # store workout/exercise data together
    workout_data.append(workout_entry)
    exercise_data.append(exercise_entry)

    # prepare lists for plotting
    dates = [w["Date"] for w in workout_data]  # gets the dates from exercise data
    times = [int(w["workout_time"]) for w in workout_data]  # get the times for the data

    sets = [int(s["Sets"]) for s in exercise_data]  # gets the sets for s in exercise_data
    reps = [int(s["Reps"]) for s in exercise_data]  # gets the reps for s in exercise_data

    if workout_id in plt.get_figlabels():
        fig = plt.figure(workout_id)
        ax1 = fig.axes[0]
        ax2 = ax1.twinx()
    else:
        fig, ax1 = plt.subplots(num=workout_id, figsize=(12, 6))
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Time (min)", color="blue")
        ax1.tick_params(axis="y", labelcolor="blue")
        ax2 = ax1.twinx()
        ax2.set_ylabel("Sets/Reps", color="red")
        ax2.tick_params(axis="y", labelcolor="red")

    # containers for the workout data an exercise data
    workout_data, exercise_data = [], []

    # add new data to workout and exercise
    workout_data.append(workout_entry)
    exercise_data.append(exercise_entry)

    # clear axes before plotting data
    ax1.cla()
    ax2.cla()

    # plot workouts
    ax1.plot(dates, times, "r-^", label='workout time (min)', linewidth=2)

    # plot sets/reps
    ax2.plot(dates, sets, "r-^", label='sets', linewidth=2)
    ax2.plot(dates, reps, "g-s", label='sets', linewidth=2, alpha=0.7)

    # format x-axis
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

    # legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    fig.tight_layout()
    plt.show()

    return fig


# -------- chatbot functionality ------------
def chat():




# -------- define tool use using harmony response model -----------

def use_tools():
    system_message = (
        SystemContent.new()
        .with_reasoning_effort(ReasoningEffort.HIGH)
        .with_conversation_start_date(str(datetime.date.today()))
    )

    developer_message = (
        DeveloperContent.new()
        .with_instructions(
            """
            You are a professional fitness coach and advisor. Your role is to provide clear, safe, 
            and actionable guidance on all aspects of health and fitness, including:
            
            - exercise science (strength training, cardio, flexibility, mobility, sport-specific training)
            - Workout programming (beginner → advanced plans, progression, periodization, body weight vs. weights, home vs. gym)
            - Nutrition (macros, calories, hydration, meal timing, supplements — with evidence-based recommendations)
            - Recovery & injury prevention (stretching, sleep, rest days, active recovery, stress management)
            - Mindset & habit building (motivation, goal setting, accountability, long-term consistency)

            Instructions for behavior:
            
            - Be conversational, motivating, and encouraging — like a real coach who adapts to the user’s fitness level and goals.
            - Tailor advice to the individual (e.g., beginner vs. advanced, specific goals like fat loss, strength, hypertrophy, or endurance).
            - Explain the “why” behind recommendations so the user learns principles, not just quick answers.
            - Stay evidence-based and safe — never recommend extreme or unsafe practices.
            - If asked for medical advice beyond general fitness, remind the user to consult a healthcare professional.
            - Offer options and flexibility — adapt advice for home workouts, limited equipment, busy schedules, or dietary restrictions.
            - Encourage tracking and measurable progress (logs, goals, reflection).
            
            Tone: Supportive, knowledgeable, and approachable — like a coach who wants the user to succeed.
            """
        )
        .with_function_tools([
            ToolDescription.new(
                "analyze",
                "analyzes workouts for how many sets, reps, weight, time taken, muscles targeted. calculates intensity level",
                parameters={
                    "type": "object",
                    # properties are all the args for the function tool
                    "properties": {
                        "sets": {
                            "type": "Integer",
                            "description": "The number of sets for the given exercise"
                        },
                        "reps": {
                            "type": "integer",
                            "description": "The number of reps for the given exercise"
                        },
                        "weight": {
                            "type": "float",
                            "description": "the amount of weight lifted in lbs"
                        },
                        "time": {
                            "type": "int",
                            "description": "the time taken for the workout"
                        },
                        "muscles_targeted": {
                            "type": "string",
                            "description": " The muscles targeted during the workout"
                        },
                    },
                    "required": ["sets", "reps"]
                },
            ),
            # tool for meal_recommender, takes the output of analyze tools as input
            ToolDescription.new(
                "meal_recommender",
                "recommends meals after a workout based on output of previous analysis tool",

                parameters={
                    "type": "object",
                    "properties": {
                        "recommended_meal": {
                            "type": "string",
                            "description": "a recommended meal for after a workout"
                        },
                        "calories": {
                            "type": "integer",
                            "description": "Total calories in the meal"
                        },
                        "macros": {
                            "type": "object",
                            "description": "Macronutrient breakdown of the meal",
                            "properties": {
                                "protein": {"type": "number", "description": "Protein in grams"},
                                "carbs": {"type": "number", "description": "Carbohydrates in grams"},
                                "fat": {"type": "number", "description": "Fat in grams"},
                            },
                            "required": ["protein", "carbs", "fat"],
                        },
                    },
                    "required": ["meal_name", "calories", "macros"],
                }
            ),
            # tool for recovery_planner
            ToolDescription.new(
                "recovery_planner",
                "plans recovery times based on sleep nutrition and exercise intensity",
                parameters={
                    "properties": {
                        "sleep": {
                            "type": "number",
                            "description": "Hours of sleep the user got the previous night",
                            "minimum": 0,
                            "maximum": 24
                        },
                        "muscle_groups": {
                            "type": "array",
                            "description": "List of muscle groups the user plans to train today",
                            "items": {
                                "type": "string",
                                "enum": [
                                    "chest",
                                    "back",
                                    "legs",
                                    "shoulders",
                                    "arms",
                                    "core",
                                    "full_body"
                                ]
                            }
                        },
                        "intensity": {
                            "type": "string",
                            "description": "Workout intensity level to tailor meal planning",
                            "enum": ["low", "moderate", "high"]
                        }
                    },
                    "required": ["sleep", "muscle_groups", "intensity"]
                }
            )
        ])
    )

    convo = Conversation.from_messages(
        [
            Message.from_role_and_content(Role.SYSTEM, system_message),
            Message.from_role_and_content(Role.DEVELOPER, developer_message),
            Message.from_role_and_content(Role.USER, "put user message (prompt) here"),
            Message.from_role_and_content(
                Role.ASSISTANT,
                'user asks: *put user message here*, we need to use analyze_workout tool'
            ).with_channel("analysis")
        ]
    )
