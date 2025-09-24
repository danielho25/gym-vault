import lmstudio as lms
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import openai
from dotenv import load_dotenv
import datetime
import re
import os
from openai import OpenAI
from openai import OpenAIError

"""
v0.0.1:
- initial chat function using tools and qwen4b model for testing

v0.0.2 09/23/25:
- reverting to older openai response format so I can use gpt-oss via different machine's lmstudio 
"""

# Global workout storage
current_workout_data = None


def collect_workout_data():
    """
    Collect workout data through simple prompts
    Returns structured workout dictionary
    """
    print("\nLet's log your workout!")
    print("=" * 40)

    # Get basic workout info
    try:
        workout_time = int(input("How long was your workout (minutes)? "))
    except ValueError:
        workout_time = 45
        print("Using default: 45 minutes")

    # Collect exercises
    exercises = {}
    exercise_count = 1
    all_muscle_groups = set()

    # Simple muscle group mapping
    muscle_map = {
        "squat": ["quads", "glutes"],
        "bench": ["chest", "shoulders", "triceps"],
        "deadlift": ["back", "hamstrings", "glutes"],
        "row": ["back", "biceps"],
        "pullup": ["back", "biceps"],
        "pull": ["back", "biceps"],
        "press": ["shoulders", "triceps"],
        "curl": ["biceps"],
        "tricep": ["triceps"],
        "dip": ["chest", "triceps"],
        "lunge": ["quads", "glutes"],
        "leg": ["quads", "hamstrings"],
        "calf": ["calves"],
        "abs": ["core"],
        "plank": ["core"]
    }

    while True:
        print(f"\nExercise #{exercise_count}")
        print("-" * 20)

        # Get exercise name
        exercise_name = input("Exercise name (or 'done' to finish): ").strip().lower()
        if exercise_name == 'done' or exercise_name == '':
            break

        try:
            # Get exercise details
            sets = int(input("Number of sets: "))
            reps = int(input("Reps per set: "))
            weight = float(input("Weight used (lbs): "))

            # Get RPE (Rate of Perceived Exertion)
            print("RPE Scale: 1-3=Very Easy, 4-6=Moderate, 7-8=Hard, 9-10=Maximum")
            rpe = int(input("RPE (1-10): "))
            rpe = max(1, min(10, rpe))  # Clamp between 1-10

            # Store exercise data as tuple: (sets, reps, weight, rpe)
            exercises[exercise_name] = (sets, reps, weight, rpe)

            # Add muscle groups
            for key, muscles in muscle_map.items():
                if key in exercise_name:
                    all_muscle_groups.update(muscles)
                    break
            else:
                all_muscle_groups.add("core")  # default if not found

            print(f"Added: {sets} sets x {reps} reps @ {weight}lbs (RPE {rpe})")
            exercise_count += 1

        except ValueError:
            print("Invalid input. Please enter numbers only.")
            continue
        except KeyboardInterrupt:
            print("\nWorkout logging cancelled.")
            return None

    if not exercises:
        print("No exercises logged.")
        return None

    # Build workout dictionary
    workout_id = f"workout_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}"
    workout_data = {
        workout_id: exercises,
        "time": workout_time,
        "muscles_targeted": ", ".join(sorted(all_muscle_groups)),
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "exercise_count": len(exercises)
    }

    # Display summary
    print("\nWorkout Summary:")
    print("=" * 40)
    print(f"Duration: {workout_time} minutes")
    print(f"Exercises: {len(exercises)}")
    print(f"Muscle Groups: {workout_data['muscles_targeted']}")
    print("\nExercise Details:")
    for name, (sets, reps, weight, rpe) in exercises.items():
        total_volume = sets * reps * weight
        print(f"• {name.title()}: {sets}x{reps} @ {weight}lbs (RPE {rpe}) - Volume: {total_volume}lbs")

    return workout_data


def analyze_workout(workout: Optional[Dict] = None) -> dict:
    """Analyze workout using global workout data if none provided"""
    global current_workout_data

    if workout is None:
        workout = current_workout_data

    if not workout:
        return {"error": "No workout data available. Please log a workout first."}

    # User estimated 1RMs for percentage calculations
    user_maxes = {
        "squat": 405, "bench": 260, "deadlift": 500,
        "row": 200, "press": 150, "curl": 100,
        "pullup": 200, "dip": 250
    }

    total_load = 0.0
    workout_time = workout.get("time", 1)
    muscle_groups = workout.get("muscles_targeted", "")

    # Parse muscle groups
    mg = set(muscle_groups.split(", ")) if muscle_groups else set()

    exercise_details = []

    # Process each exercise
    for workout_id, exercises in workout.items():
        if isinstance(exercises, dict):
            for exercise_name, exercise_data in exercises.items():
                if isinstance(exercise_data, tuple) and len(exercise_data) == 4:
                    sets, reps, weight, rpe = exercise_data

                    # Calculate volume and load
                    volume = sets * reps * weight
                    intensity_factor = rpe / 10
                    base_load = volume * intensity_factor

                    # Adjust for percentage of estimated max
                    max_weight = None
                    for max_exercise, max_val in user_maxes.items():
                        if max_exercise in exercise_name.lower():
                            max_weight = max_val
                            percent_of_max = (weight / max_val) * 100
                            # Bonus for higher percentage work
                            base_load *= (1 + (percent_of_max / 100) * 0.5)
                            break

                    total_load += base_load

                    exercise_details.append({
                        "name": exercise_name.title(),
                        "sets": sets,
                        "reps": reps,
                        "weight": weight,
                        "rpe": rpe,
                        "volume": volume,
                        "load_contribution": round(base_load, 1),
                        "estimated_1rm_percent": round((weight / max_weight * 100), 1) if max_weight else None
                    })

    if not exercise_details:
        return {"error": "No valid exercises found in workout"}

    # Calculate final metrics
    density = total_load / max(workout_time, 1)  # Load per minute
    muscle_work_multiplier = 1 + (len(mg) - 1) * 0.15  # Bonus for more muscle groups
    final_intensity = density * muscle_work_multiplier

    # Classify intensity level
    if final_intensity > 100:
        intensity_level = "Very High"
    elif final_intensity > 60:
        intensity_level = "High"
    elif final_intensity > 30:
        intensity_level = "Moderate"
    else:
        intensity_level = "Light"

    return {
        "total_load": round(total_load, 1),
        "density": round(density, 2),
        "muscle_work_multiplier": round(muscle_work_multiplier, 2),
        "intensity_score": round(final_intensity, 1),
        "intensity_level": intensity_level,
        "workout_time": workout_time,
        "exercises_count": len(exercise_details),
        "muscle_groups": sorted(list(mg)),
        "exercise_breakdown": exercise_details,
        "total_volume": sum(ex["volume"] for ex in exercise_details)
    }


def meal_rec(workout: Optional[Dict] = None, macros: Optional[Dict] = None) -> dict:
    """Meal recommendations based on workout analysis"""
    global current_workout_data

    if workout is None:
        workout = current_workout_data

    if not workout:
        return {"error": "No workout data for meal recommendations"}

    # Default macro targets
    if macros is None:
        macros = {
            "total_cals": 2200,
            "macros": {
                "protein": 160,  # ~30% calories
                "carbs": 220,  # ~40% calories
                "fat": 75  # ~30% calories
            }
        }

    # Analyze the workout first
    analysis = analyze_workout(workout)
    if "error" in analysis:
        return analysis

    intensity_score = analysis["intensity_score"]
    workout_time = analysis["workout_time"]
    muscle_groups = analysis["muscle_groups"]

    # Adjust macros based on intensity
    base_protein = macros["macros"]["protein"]
    base_carbs = macros["macros"]["carbs"]
    base_fat = macros["macros"]["fat"]

    if intensity_score > 60:  # High intensity
        protein_boost = 1.25
        carb_boost = 1.3
        recommendation = "High intensity workout - prioritize post-workout nutrition!"
    elif intensity_score > 30:  # Moderate intensity
        protein_boost = 1.15
        carb_boost = 1.15
        recommendation = "Solid workout - good nutrition timing will help recovery"
    else:  # Light intensity
        protein_boost = 1.0
        carb_boost = 1.0
        recommendation = "Light session - maintain your normal eating schedule"

    return {
        "intensity_analysis": {
            "score": intensity_score,
            "level": analysis["intensity_level"],
            "workout_duration": workout_time
        },
        "macro_recommendations": {
            "protein_g": round(base_protein * protein_boost),
            "carbs_g": round(base_carbs * carb_boost),
            "fat_g": base_fat,
            "total_calories": macros["total_cals"]
        },
        "timing_advice": {
            "pre_workout": "Light carbs 30-60min before" if intensity_score > 30 else "Not critical",
            "post_workout": "Protein + carbs within 30min" if intensity_score > 60 else "Within 2 hours is fine",
            "hydration": f"{2.5 + (intensity_score / 50)} liters today"
        },
        "recommendation": recommendation,
        "muscle_groups_trained": muscle_groups
    }


def recovery(sleep: float, muscle_groups: Optional[List] = None, intensity_level: str = "moderate") -> dict:
    """Recovery recommendations"""
    global current_workout_data

    # Use workout data if available
    if muscle_groups is None and current_workout_data:
        analysis = analyze_workout(current_workout_data)
        if "muscle_groups" in analysis:
            muscle_groups = analysis["muscle_groups"]
            intensity_level = analysis["intensity_level"].lower()
        else:
            muscle_groups = ["core"]
    elif muscle_groups is None:
        muscle_groups = ["core"]

    # Sleep quality score
    sleep_score = min(100, max(0, (sleep / 8) * 100))

    # Recovery time by muscle group (hours)
    recovery_times = {
        "chest": 48, "back": 48, "shoulders": 36,
        "quads": 48, "hamstrings": 48, "glutes": 48,
        "biceps": 36, "triceps": 36, "calves": 24, "core": 24
    }

    # Intensity multipliers
    intensity_multipliers = {
        "light": 0.8, "moderate": 1.0,
        "high": 1.3, "very high": 1.5
    }

    multiplier = intensity_multipliers.get(intensity_level, 1.0)

    # Calculate recovery needs
    max_recovery_hours = 0
    for muscle in muscle_groups:
        base_time = recovery_times.get(muscle, 24)
        adjusted_time = base_time * multiplier
        max_recovery_hours = max(max_recovery_hours, adjusted_time)

    # Sleep impact on recovery
    if sleep < 6:
        sleep_penalty = 1.4
        sleep_advice = "Poor sleep will significantly delay recovery"
    elif sleep < 7:
        sleep_penalty = 1.2
        sleep_advice = "Suboptimal sleep may slow recovery"
    else:
        sleep_penalty = 1.0
        sleep_advice = "Good sleep supports optimal recovery"

    final_recovery_hours = max_recovery_hours * sleep_penalty

    return {
        "sleep_analysis": {
            "hours": sleep,
            "score": round(sleep_score),
            "impact": sleep_advice
        },
        "recovery_timeline": {
            "base_hours": round(max_recovery_hours),
            "with_sleep_factor": round(final_recovery_hours),
            "ready_for_similar_workout": f"{round(final_recovery_hours / 24, 1)} days"
        },
        "recommendations": {
            "hydration_liters": 3.0 + (0.5 if intensity_level in ["high", "very high"] else 0),
            "next_workout_intensity": "Reduce intensity" if sleep < 6 and intensity_level == "high" else "Normal progression",
            "focus_areas": muscle_groups
        },
        "muscle_groups_trained": muscle_groups,
        "intensity_level": intensity_level
    }


# open ai old method (not really using tools but openai wont let me connect to a better machine with open gpt)

# load env var to get the connection
load_dotenv()

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

analyze_prompt = """
Given the analysis data from a workout (intensity, load, density, volume, exercises, and muscle groups), write a short, encouraging summary in plain English.

Guidelines:
- Start with an overall assessment (Light / Moderate / High / Very High intensity).
- Mention key stats: total volume, total load, and workout time (if provided).
- Highlight how many exercises were done and the main muscle groups trained.
- Be motivating and supportive — like a coach giving quick feedback.
- Keep it to 3–5 sentences, maximum.
- Do not output raw numbers in a list — weave them naturally into the summary."""

meal_rec_prompt = """
Given the meal_rec() data (intensity, macro recommendations, timing advice, and muscle groups trained), write a short, supportive nutrition summary in plain English.

Guidelines:
- Begin with the overall recommendation (e.g., high intensity = emphasize recovery fueling).
- Mention protein, carbs, and fat in grams, but weave them naturally into sentences (not a raw list).
- Include key timing advice (pre/post-workout nutrition and hydration).
- Tailor the tone to intensity level (light = maintain, moderate = solid recovery, high = prioritize refueling).
- Be encouraging, practical, and evidence-based.
- Keep the response 3–5 sentences, maximum.
- Do not just restate numbers — explain why they matter for recovery and performance."""

recovery_prompt = """
Given the recovery() data (sleep quality, recovery timeline, hydration, and recommendations), write a short, encouraging recovery summary in plain English.

Guidelines:
- Start with an assessment of sleep and its impact on recovery. 
- Mention how long it may take before the trained muscles are fully recovered (in hours or days).
- Give practical advice: hydration, when to train again, and whether to adjust workout intensity.
- Tailor the tone to the sleep quality and workout intensity (e.g., supportive if sleep was poor, motivating if sleep was good).
- Keep the response 3–5 sentences, maximum.
- Always be positive, actionable, and safety-focused.
"""


def connect_to_gpt(prompt_txt: str, include_context: bool = False):
    global current_workout_data
    # model parameters:
    llm_con = os.getenv("LMS_CONN")
    default_system_prompt = coach_mike

    client = OpenAI(
        base_url=llm_con,
        api_key="a"
    )

    full_prompt = prompt_txt

    if include_context and current_workout_data:
        # Add workout context to the prompt
        workout_analysis = analyze_workout(current_workout_data)
        context = f"\n\nCurrent workout context: {json.dumps(workout_analysis, indent=2)}"
        full_prompt = prompt_txt + context

    history = [
        {"role": "system",
         "content": coach_mike},
        {"role": "user",
         "content":full_prompt}
    ]

    try:
        completion = client.chat.completions.create(
            model="unsloth/gpt-oss-120b",
            messages=history,
            max_tokens=1500,
            frequency_penalty=0.7,
            reasoning_effort="medium",
            temperature=1.0,
        )

        return completion.choices[0].message.content.strip()
    except openai.APIConnectionError as e:
        return f"OpenAI Connection error: the server could not be reached: {e}"
    except openai.APIStatusError as e:
        return f"OpenAI Rate Limit Error: A 429 status code was received: {e}"
    except openai.APIError as e:
        return f"API error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


def process_user_command(user_input: str) -> str:
    """
    Process user commands and route to appropriate functions

    Args:
        user_input: User's input string

    Returns:
        Response string
    """
    global current_workout_data

    user_input = user_input.strip().lower()

    # Special commands
    if user_input in ['log workout', 'workout', 'log']:
        workout_data = collect_workout_data()
        if workout_data:
            current_workout_data = workout_data
            # analysis = analyze_workout(workout_data)
            return f"Workout logged successfully!"
        else:
            return "Workout logging was cancelled or failed."

    elif user_input in ['analyze', 'analysis']:
        if current_workout_data:
            analysis = analyze_workout(current_workout_data)
            analysis_chat = connect_to_gpt(analyze_prompt, analysis)
            return analysis_chat
        else:
            return "No workout data available. Please log a workout first using 'log workout'."

    elif user_input in ['meal', 'nutrition', 'macros']:
        if current_workout_data:
            meal_recs = meal_rec(current_workout_data)
            meal_rec_chat = connect_to_gpt(meal_rec_prompt, meal_recs)
            return meal_rec_chat
        else:
            return "No workout data available for meal recommendations. Please log a workout first."

    elif user_input.startswith('recovery'):
        # Parse sleep hours if provided (e.g., "recovery 7.5")
        try:
            parts = user_input.split()
            sleep_hours = float(parts[1]) if len(parts) > 1 else 7.0
        except (IndexError, ValueError):
            sleep_hours = 7.0

        recovery_plan = recovery(sleep_hours)
        recovery_resp = connect_to_gpt(recovery_prompt, recovery_plan)
        return f"Recovery Plan based on {sleep_hours} of sleep: {recovery_resp}"

    elif user_input in ['help', 'commands']:
        return """Available commands:

• 'log workout' - Start the workout logging process
• 'analyze' - Show analysis of current workout
• 'meal' - Get meal recommendations based on workout
• 'recovery [hours]' - Get recovery plan (optionally specify sleep hours)
• 'help' - Show this help message
• 'quit' - Exit the program
• Any other text will be sent to Coach Mike for fitness advice

Current workout logged: {'Yes' if current_workout_data else 'No'}"""

    elif user_input in ['quit', 'exit', 'q']:
        return "QUIT"

    else:
        # Send to LLM with workout context if available
        include_context = current_workout_data is not None
        return connect_to_gpt(user_input, include_context=include_context)

def main():
    """main program chat loop"""
    print("Welcome! I'm Coach Mike, your personal workout coach!")
    print("-"*50)
    print("Type 'help' for available commands or just ask me anything about fitness!")
    print("Type 'quit' to exit.")
    print("-" * 50)

    conversation_history = []
    while True:
        try:
            print("You: ")
            user_input = input().strip()
            if not user_input:
                continue

            conversation_history.append(user_input)  # store user messages
            response = process_user_command(user_input)

            if response == "q" or response == "quit":
                print("thanks for using coach mike!")
                break

            print("Coach Mike: ", response)
            conversation_history.append(response)

        except KeyboardInterrupt:
            print(f"keyboard interrupt: thanks for using coach mike!")
            break
        except Exception as e:
            print(f"an error occured: {e}")

if __name__ == "__main__":
    main()
