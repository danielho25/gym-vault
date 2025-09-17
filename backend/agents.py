import lmstudio as lms
import json
import time
from typing import Dict, Any, List
from collections import defaultdict
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from dotenv import load_dotenv
import os
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

load_dotenv()

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
    workout_id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_date DATE NOT NULL,
    workout_time TIME NOT NULL
);
"""

create_exercise_table = """
CREATE TABLE IF NOT EXISTS workout_exercise (
    exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INT NOT NULL,
    exercise_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (workout_id) REFERENCES workout(workout_id) ON DELETE CASCADE
);
"""

database = 'workout_data.db'
encoding = load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)


def create_table():
    try:
        with sqlite3.connect(database) as conn:
            cursor = conn.cursor()
            cursor.execute(create_workout_table)
            cursor.execute(create_exercise_table)
            conn.commit()
            print("Tables created successfully!")
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
    dates = [workout_entry["Date"]]  # gets the dates from exercise data
    times = [int(exercise_entry["workout_time"])]  # get the times for the data

    sets = [int(exercise_entry["Sets"])]  # gets the sets for s in exercise_data
    reps = [int(exercise_entry["Reps"])]  # gets the reps for s in exercise_data

    for date in dates:
        date_objects = [datetime.datetime.strptime(date, "%Y=%m-%d")]

    if workout_id in plt.get_figlabels():
        fig = plt.figure(workout_id)
        ax1 = fig.axes[0]
        ax2 = ax1.twinx()
        ax1.clear()
        ax2.clear()
    else:
        fig, ax1 = plt.subplots(num=workout_id, figsize=(12, 6))
        ax2 = ax1.twinx()

    ax1.set_xlabel("Date")
    ax1.set_ylabel("Time (min)", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")
    ax2.set_ylabel("Sets/Reps", color="red")
    ax2.tick_params(axis="y", labelcolor="red")

    # plot workouts
    ax1.plot(dates, times, "b-o", label='workout time (min)', linewidth=2)

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


# ---------- Tools -------------
# example functions to simulate a workout
example_workout = {
    "workout_20251109": {
        "squat": [3, 8, 225, 8],
        "bench": [2, 5, 100, 6]
    },
    "time": 45,
    "muscles_targeted": "legs, chest, shoulders"
}


def analyze_workout(workout: dict) -> dict:
    """
    This function needs to:
        - read all data from the workout
        - calculate intensity level
    :return: score of the workout
    """
    user_maxes = {
        "squat": 405,
        "bench": 260,
        "deadlift": 500
    }

    total_load = 0.0
    workout_time = workout.get("time", 1)  # avoid divide by zero
    muscle_groups = workout.get("muscles_targeted", "")

    # determine how many muscle groups
    mg = set(muscle_groups)

    for workout_id, exercises in workout.items():
        if isinstance(exercises, dict):  # only dive into exercise dicts
            for exercise, (sets, reps, weight, rpe) in exercises.items():
                base_load = (sets * reps * weight) * (rpe / 10)

                # track % of max lifted
                if exercise in user_maxes:
                    percent_of_max = weight / user_maxes[exercise]
                    base_load += (base_load * percent_of_max * 0.5)

                total_load += base_load

    # determine how much work done in a span of time
    density = total_load / workout_time

    # determine the difficulty of workouts (compound vs isolation)
    if mg:
        muscle_work = 1 + 0.1 * (len(mg) - 1)
    else:
        muscle_work = 1.0

    # determine total score
    intensity = density * muscle_work

    workout_analysis = {
        "total load": total_load,
        "density": density,
        "muscle work": muscle_work,
        "intensity": intensity
    }

    return workout_analysis


# -------- meal recommender ---------

# with the frontend, the app will have max cals and macros based on user suggestions.
# here is a simulated dictionary structure for testing:

daily_nutr = {
    "total_cals": 2000,
    "macros": {
        "protein": 50,
        "carbs": 100,
        "fat": 30
    }
}


def meal_rec(workout: dict, macros: dict) -> dict:
    intensity = analyze_workout(example_workout)
    total_cals = daily_nutr.get("total_cals")
    workout_time = workout.get("time", 45)
    muscle_groups = workout.get("")

    # get data
    macro_data = macros.get("macros", {})
    protein_grams = macro_data.get("protein", 0)
    carbs_grams = macro_data.get("carbs", 0)
    fat_grams = macro_data.get("fat", 0)

    calculated_cals = (protein_grams * 4) + (carbs_grams * 4) + (fat_grams * 9)

    # check if cals match
    if calculated_cals != total_cals:
        print(
            f"Error: the amount of calories provided ({calculated_cals}) does not match total daily goals: {total_cals}")

    # build the dictionary for response
    nutrition_info = {
        "intensity": intensity,
        "total cals": total_cals,
        "workout time": workout_time,
        "muscle group": muscle_groups,
        "macro data": macro_data,
        "protein (g)": protein_grams,
        "carbohydrates (g)": carbs_grams,
        "fat (g)": fat_grams
    }

    return nutrition_info


# --------- recovery recommendation ---------
def recovery(sleep: float, muscle_groups: list[str], intensity: str) -> dict:
    if sleep >= 8:
        sleep_score = 100
    elif sleep >= 7:
        sleep_score = 85
    elif sleep >= 6:
        sleep_score = 65
    elif sleep >= 5:
        sleep_score = 50
    else:
        sleep_score = 25

    muscle_recovery_times = {
        "chest": {"recovery_time_hrs": 48, "intensity_mult": 1.4},
        "back": {"recovery_time_hrs": 48, "intensity_mult": 1.4},
        "shoulders": {"recovery_time_hrs": 36, "intensity_mult": 1.1},
        "triceps": {"recovery_time_hrs": 36, "intensity_mult": 1.1},
        "biceps": {"recovery_time_hrs": 36, "intensity_mult": 1.1},
        "quads": {"recovery_time_hrs": 48, "intensity_mult": 1.6},
        "hamstrings": {"recovery_time_hrs": 48, "intensity_mult": 1.6},
        "glutes": {"recovery_time_hrs": 48, "intensity_mult": 1.6},
        "core": {"recovery_time_hrs": 24, "intensity_mult": 1.2},
    }

    intensity_levels = {
        "low": {"multiplier": 0.8, "stress_level": 25},
        "medium": {"multiplier": 1.0, "stress_level": 50},
        "high": {"multiplier": 1.4, "stress_level": 75},
        "max": {"multiplier": 1.8, "stress_level": 90}
    }

    # recovery analysis
    max_recovery_hours, total_stress = 0, 0

    for muscle in muscle_groups:
        if muscle in muscle_recovery_times:
            base_recovery_time = muscle_recovery_times[muscle]["recovery_time_hrs"]
            muscle_multiplier = muscle_recovery_times[muscle]["intensity_mult"]
            intensity_level = intensity_levels[intensity]["multiplier"]

            adjusted_recovery_time = base_recovery_time * muscle_multiplier * intensity_level
            max_recovery_hours = max(max_recovery_hours, adjusted_recovery_time)
            total_stress += muscle_multiplier * intensity_level

    # calculate sleep effect
    sleep_deficit = max(0, 8.0 - sleep)
    recovery_delay_factor = 1 + (sleep_deficit * 0.15)  # for each hour of sleep lost, performance drops 15%
    rec_recovery_hours = max_recovery_hours * recovery_delay_factor

    # hydration needs
    base_hydration_liters = 2.5
    hydration_levels = {
        "low": 0.3,  # if intensity is low, 0.3 extra liters, so on so forth for each level
        "moderate": 0.6,
        "high": 1.0
    }

    recommended_hydration = base_hydration_liters + hydration_levels[intensity]

    # recovery strategies
    recovery_strategies = []
    if intensity == "high":
        recovery_strategies.extend([
            "active recovery", "rest", "hydration", "mobility exercises"
        ])

    for muscle in muscle_groups:
        if muscle == "quads" or muscle == "hamstrings" or muscle == "glutes":
            recovery_strategies.extend([
                "hip, lower back mobility", "low joint impact exercises", "gentle massage"
            ])
        elif muscle == "shoulders" or muscle == "biceps" or muscle == "triceps":
            recovery_strategies.extend([
                "shoulder mobility", "elbow and wrist health"
            ])
        elif muscle == "chest" or muscle == "back":
            recovery_strategies.extend([
                "back mobility", "shoulder mobility and injury prevention", "elbow and wrist health",
                "strengthen low back"
            ])
        else:
            recovery_strategies.extend([
                "rest and recovery", "light massage"
            ])

        # risk assessments
        risk_factors = []
        risk_score = 0.0

        if sleep < 6 and intensity == "high":
            risk_factors.extend([
                "higher risk of injury from heavy lifts when sleep-deprived",
                "poor recovery and over-training from lack of sleep",
                "hormonal imbalance and weakened immunity with high intensity"
            ])
            risk_score += 3

        elif (sleep < 7 or sleep < 8) and intensity == "high":
            risk_factors.extend([
                "reduced strength and endurance from limited sleep",
                "slower muscle recovery between high intensity sessions",
                "higher fatigue leading to poor lifting form and mistakes"
            ])
            risk_score += 2

        elif sleep < 6 and intensity == "moderate":
            risk_factors.extend([
                "slower recovery even from moderate training when sleep-deprived",
                "increased fatigue reducing workout quality and consistency",
                "elevated stress and poor adaptation to training stimulus"
            ])
            risk_score += 1

        else:
            risk_factors.append("Even with minor risk, monitor recovery and adjust training accordingly")
            risk_score += 0.5

        # structured data
        recovery_analysis = {
            "sleep_and_stress": {
                "sleep_score": sleep_score,
                "sleep_deficit": sleep_deficit,
                "rec_recovery_hours": round(rec_recovery_hours),
                "total_stress": round(total_stress, 2),
                "intensity_stress_score": intensity_levels[intensity]["stress_level"]
            },

            "phys_needs": {
                "hydration": round(recommended_hydration),
                "muscles_trained": muscle_groups,
                "recovery_focus": max(muscle_groups,
                                      key=lambda x: muscle_recovery_times.get(x, {}).get("recovery_hours",
                                                                                         0)) if muscle_groups else None
            },

            "recovery_strategies": {
                "strategies": recovery_strategies,
                "training_recs": {
                    "time_until_mg_recovered": round(adjusted_recovery_time),
                    "intensity_rec": "low" if risk_score > 40 else "moderate" if risk_score > 20 else "maintain"
                }
            }
        }

        return recovery_analysis


coach_mike = """You are Coach Mike, an experienced fitness coach and nutritionist. Your role is to provide clear, safe, and actionable guidance on all aspects of health and fitness, including:

- Exercise science (strength training, cardio, flexibility, mobility, sport-specific training)
- Workout programming (beginner → advanced plans, progression, periodization, body weight vs. weights, home vs. gym)
- Nutrition (macros, calories, hydration, meal timing, supplements — with evidence-based recommendations)
- Recovery & injury prevention (stretching, sleep, rest days, active recovery, stress management)
- Mindset & habit building (motivation, goal setting, accountability, long-term consistency)

TOOL USAGE INSTRUCTIONS:
- Always use the analyze tool first when a user describes a workout.
- Use meal_recommender after analyzing a workout if nutrition questions arise or macros are discussed.
- Use recovery_planner when discussing rest, sleep, or training frequency.
- Provide specific, actionable advice based on tool outputs.

BEHAVIOR & TONE:
- Be conversational, motivating, and encouraging — like a real coach who adapts to the user’s fitness level and goals.
- Explain the “why” behind recommendations so the user learns principles, not just quick answers.
- Stay evidence-based and safe — never recommend extreme or unsafe practices.
- Tailor advice to the individual (beginner vs. advanced, goals like fat loss, strength, hypertrophy, endurance).
- Offer flexibility — adapt advice for home workouts, limited equipment, busy schedules, or dietary restrictions.
- Encourage tracking and measurable progress (logs, goals, reflection).
- If asked for medical advice beyond general fitness, remind the user to consult a healthcare professional.

STYLE:
- Tone: Supportive, knowledgeable, approachable — like a coach who wants the user to succeed.
- Response length: Maximum 3 natural English paragraphs.
- Always be encouraging, data-driven, and safety-focused."""


# -------- define tool use using harmony response model -----------
def chat_with_coach():
    # --- Build system & developer messages ---
    system_message = (
        SystemContent.new()
        .with_reasoning_effort(ReasoningEffort.HIGH)
        .with_conversation_start_date(str(datetime.date.today()))
        # .with_instructions(coach_mike)
        # .with_response_format("harmony")
        # .with_safety_guidelines([
        #     "always prioritize user safety in exercise recommendations",
        #     "never recommend dangerous or extremely difficult exercises that could cause injury",
        #     "suggest consulting healthcare advisors for medical concerns"
        # ])
    )

    developer_message = (
        DeveloperContent.new()
        .with_instructions("""
        TOOL EXECUTION RULES:
            1. When user mentions a workout, ALWAYS use the analyze tool first
            2. For nutrition questions, use meal_recommender with workout data + macro targets  
            3. For recovery questions, use recovery_planner with sleep + muscles + intensity
            4. Chain tools logically: analyze → meal_recommender and/or recovery_planner
            5. Always explain tool results in user-friendly language

            RESPONSE FORMAT:
            - Use <reasoning> tags to show your thinking process
            - Use <tool_call> tags for function calls
            - Provide clear, actionable advice based on tool outputs
        """)
        .with_function_tools([
            # --- analyze tool ---
            ToolDescription.new(
                "analyze",
                "analyzes workouts for how many sets, reps, weight, time taken, muscles targeted. calculates intensity level",
                parameters={
                    "type": "object",
                    "properties": {
                        "workout": {
                            "type": "object",
                            "description": "Complete workout data including exercises and metadata",
                            "properties": {
                                "time": {
                                    "type": "integer",
                                    "description": "Total workout time in minutes"
                                },
                                "muscles_targeted": {
                                    "type": "string",
                                    "description": "Comma-separated list of muscles targeted (e.g. 'legs, chest, shoulders')"
                                }
                            },
                            "additionalProperties": {
                                "type": "object",
                                "description": "Exercise data keyed by workout session ID",
                                "additionalProperties": {
                                    "type": "array",
                                    "description": "Exercise performance data: [sets, reps, weight, rpe]",
                                    "items": {"type": "integer"},
                                    "minItems": 4,
                                    "maxItems": 4
                                }
                            },
                            "required": ["time", "muscles_targeted"]
                        }
                    },
                    "required": ["workout"]
                }
            ),

            # --- meal_recommender tool ---
            ToolDescription.new(
                "meal_recommender",
                "recommends meals after a workout based on workout data and macro targets",
                parameters={
                    "type": "object",
                    "properties": {
                        "workout": {
                            "type": "object",
                            "description": "Workout data from analyze tool output or user input",
                            "properties": {
                                "time": {"type": "integer", "description": "Workout duration in minutes"},
                                "muscles_targeted": {"type": "string", "description": "Muscles worked during workout"}
                            }
                        },
                        "macros": {
                            "type": "object",
                            "description": "Daily macro and calorie targets",
                            "properties": {
                                "total_cals": {
                                    "type": "integer",
                                    "description": "Total daily calorie target"
                                },
                                "macros": {
                                    "type": "object",
                                    "description": "Daily macro targets in grams",
                                    "properties": {
                                        "protein": {"type": "number", "description": "Daily protein target in grams"},
                                        "carbs": {"type": "number", "description": "Daily carb target in grams"},
                                        "fat": {"type": "number", "description": "Daily fat target in grams"}
                                    },
                                    "required": ["protein", "carbs", "fat"]
                                }
                            },
                            "required": ["total_cals", "macros"]
                        }
                    },
                    "required": ["workout", "macros"]
                }
            ),

            # --- recovery_planner tool ---
            ToolDescription.new(
                "recovery_planner",
                "plans recovery strategy based on sleep, muscle groups trained, and workout intensity",
                parameters={
                    "type": "object",
                    "properties": {
                        "sleep": {
                            "type": "number",
                            "description": "Hours of sleep the user got the previous night",
                            "minimum": 0,
                            "maximum": 24
                        },
                        "muscle_groups": {
                            "type": "array",
                            "description": "List of muscle groups trained in the workout",
                            "items": {
                                "type": "string",
                                "enum": [
                                    "chest", "back", "shoulders", "triceps", "biceps",
                                    "quads", "hamstrings", "glutes", "core"
                                ]
                            }
                        },
                        "intensity": {
                            "type": "string",
                            "description": "Workout intensity level",
                            "enum": ["low", "medium", "high", "max"]
                        }
                    },
                    "required": ["sleep", "muscle_groups", "intensity"]
                }
            )
        ])
    )

    # --- Start conversation ---
    convo = Conversation.from_messages([
        Message.from_role_and_content(Role.SYSTEM, system_message),
        Message.from_role_and_content(Role.DEVELOPER, developer_message),
        Message.from_role_and_content(Role.USER, "Hi Coach Mike, I just finished a heavy workout!")
    ])

    return convo


# -------- harmony response loop ---------
# create client for lmstudios
client = OpenAI(
    base_url=os.getenv("LMSTUDIO_CONN"),
    api_key="not-needed"
)

# --------- map tools to function calls ----------

tool_map = {
    "analyze": analyze_workout,
    "meal_recommender": meal_rec,
    "recovery_planner": recovery
}


def execute_tool_call(tool_name: str, params: dict):
    if tool_name not in tool_map:
        raise ValueError(f"Error: unknown tool {tool_name} was called!")

    function = tool_map[tool_name]

    try:
        if tool_name == "analyze":
            return function(params["workout"])
        elif tool_name == "meal_recommender":
            return function(params["workout"], params["macros"])
        elif tool_name == "recovery_planner":
            return function(params["sleep"], params["muscle_groups"], params["intensity"])
    except Exception as e:
        return {"error": f"tool execution failed: {e}"}


def harmony_messages(convo):
    messages = []
    for m in convo.messages:
        # Using role.value to map Harmony roles to LM Studio roles
        role = m.role.value if hasattr(m.role, "value") else m.role
        content = m.content.text if hasattr(m.content, "text") else m.content
        messages.append({"role": role, "content": content})
    return messages


def detect_tool_usage(text: str) -> list:
    tools_used = []
    workout_kw = ["workout", "trained", "lifted", "exercise", "sets", "reps", "weight"]
    nutrition_keywords = ["food", "eat", "nutrition", "meal", "macros", "calories", "protein", "carbs"]
    recovery_keywords = ["recovery", "sleep", "rest", "hydration", "sore", "tired", "fatigue"]
    for kw in workout_kw:
        if kw in text.lower():
            tools_used.append("analyze")
    for kw in nutrition_keywords:
        if kw in text.lower():
            tools_used.append("meal_recommender")
    for kw in recovery_keywords:
        if kw in text.lower():
            tools_used.append("recovery_planner")

    return tools_used


def chat_loop(convo):
    while True:
        user_input = input("You: ")
        if user_input.lower() in {"quit", "exit", "q", "e"}:
            print("Got it! Exiting Chat")
            break

        convo.messages.append(
            Message.from_role_and_content(Role.USER, user_input)
        )

        tools_needed = detect_tool_usage(user_input)

        # messages = harmony_messages(convo)
        resp = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=convo
        )

        #  get reply:
        reply = resp.choices[0].message
        text = reply.get("content", "")

        for tool_name in tools_needed:
            try:
                # check if assistant wants to access tool (keyword search)
                if "analyze" or "analyze_workout" in text:
                    tool_result = execute_tool_call("analyze_workout", {"workout": example_workout})
                    convo.messages.append(
                        Message.from_role_and_content(Role.ASSISTANT, json.dumps(tool_result))
                    )
                    print("Coach Mike (tool output):", json.dumps(tool_result))
                elif "what food should i eat" or "nutrition" or "macros" or "meal" in text:
                    tool_result = execute_tool_call("meal_recommender", {"workout": example_workout})
                    convo.messages.append(
                        Message.from_role_and_content(Role.ASSISTANT, json.dumps(tool_result))
                    )
                    print("Coach Mike (tool output):", json.dumps(tool_result))
                elif "plan recovery" or "sleep" or "hydration" in text:
                    tool_result = execute_tool_call("recovery_planner",
                                                    {"sleep": 7.5, "muscle_groups": ["legs", "chest", "shoulders"],
                                                     "intensity": "high"})
                    convo.messages.append(
                        Message.from_role_and_content(Role.ASSISTANT, json.dumps(tool_result))
                    )
                    print("Coach Mike (tool output):", json.dumps(tool_result))

                if text:
                    print("Coach Mike (tool output):", text)
                    convo.messages.append(Message.from_role_and_content(Role.ASSISTANT, text))
            except Exception as e:
                print(f"error: failed to execute {tool_name}")

            try:
                messages = harmony_messages(convo)
                resp = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=convo
                )

                reply = resp.choices[0].message.content
                if reply:
                    print(f"Coach Mike: {reply}")
                    convo.messages.append(Message.from_role_and_content(Role.ASSISTANT, reply))
            except Exception as e:
                print(f"error getting response: {e}")
                print("Coach Mike: Sorry, Im having connection issues right now. Please try again later!")



# -------- main function --------
def main():
    print("starting chatbot test...")
    # test code
    try:
        print("database test")
        if create_table():
            print("Tables created succesfully!")
        else:
            print("database table creation failed!")
            return

        # test tools
        print("testing tools...")
        print("-" * 30)

        analysis_results = analyze_workout(example_workout)
        print(f"analysis results: {analysis_results}")

        meal_results = meal_rec(example_workout, daily_nutr)
        print(f"meal rec results: {meal_results}")

        recovery_plan = recovery(7.5, ["chest", "shoulders", "triceps"], "high",)
        print(f"recovery results: {recovery_plan}")

        # Test database operations
        print("\n💾 Testing database operations...")
        if store_workout():
            print("✅ Workout stored successfully!")
        else:
            print("❌ Workout storage failed!")

        # Start the chat conversation
        print("\n🤖 Initializing Coach Mike chat system...")
        print("-" * 50)

        # Create the conversation
        convo = chat_with_coach()

        if convo:
            print("✅ Chat system initialized!")
            print("\n💬 Starting interactive chat...")
            print("Commands: 'quit', 'exit', 'q', or 'e' to exit")
            print("Try asking about:")
            print("  - 'I just did squats and bench press'")
            print("  - 'What should I eat after my workout?'")
            print("  - 'I only got 6 hours of sleep, should I train?'")
            print("  - 'How should I recover from today's workout?'")
            print("-" * 50)

            # Start the chat loop
            chat_loop(convo)
        else:
            print("❌ Failed to initialize chat system!")

    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        print("Make sure you have:")
        print("  1. LM Studio running with gpt-oss-20b model loaded")
        print("  2. Correct LMSTUDIO_CONN in your .env file")
        print("  3. All required packages installed")


if __name__ == "__main__":
    print("🚀 Coach Mike Fitness Assistant")
    print("=" * 50)
    main()
