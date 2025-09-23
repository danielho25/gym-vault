import lmstudio as lms
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from dotenv import load_dotenv
import datetime
import re


# Global workout storage
current_workout_data = None


def collect_workout_data():
    """
    Collect workout data through simple prompts
    Returns structured workout dictionary
    """
    print("\n🏋️  Let's log your workout!")
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

            print(f"✅ Added: {sets} sets x {reps} reps @ {weight}lbs (RPE {rpe})")
            exercise_count += 1

        except ValueError:
            print("❌ Invalid input. Please enter numbers only.")
            continue
        except KeyboardInterrupt:
            print("\n⏹️  Workout logging cancelled.")
            return None

    if not exercises:
        print("❌ No exercises logged.")
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
    print("\n📊 Workout Summary:")
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

def remove_thinking(text):
    # Remove everything between <think> and </think> tags
    cleaned_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return cleaned_text.strip()

# Coach Mike system prompt
coach_mike = """You are Coach Mike, an experienced personal trainer and fitness coach.

You have access to these tools:
- analyze_workout(): Analyzes the user's logged workout data
- meal_rec(): Provides nutrition recommendations based on their workout
- recovery(): Gives recovery advice based on sleep and workout intensity

The user has already logged their workout data. When they ask questions, use the appropriate tools to give them specific, evidence-based advice.

Keep your responses:
- Encouraging and motivational
- Specific to their actual workout data
- Evidence-based and practical
- 2-3 paragraphs maximum
- Include specific numbers from the analysis when relevant"""

chat_buffer = []
response_buffer = []

def collect_fragment(fragment, round_index=0):
    """Collect fragments without printing - standalone function"""
    if hasattr(fragment, 'content'):
        response_buffer.append(fragment.content)
    else:
        response_buffer.append(str(fragment))

def chat_loop():
    """Main chat loop with Coach Mike"""
    global current_workout_data

    print("🏋️  Welcome to Coach Mike's Workout Assistant!")
    print("=" * 50)

    # Collect workout data first
    current_workout_data = collect_workout_data()

    if not current_workout_data:
        print("❌ No workout data collected. Exiting.")
        return

    print(f"\n✅ Workout logged successfully!")
    print("💬 Now you can chat with Coach Mike about your training!")
    print("Ask things like:")
    print("• 'How was my workout?'")
    print("• 'What should I eat after this?'")
    print("• 'How long should I rest before my next workout?'")
    print("• 'I got 7 hours of sleep, when can I train again?'")

    model = lms.llm("qwen/qwen3-4b-thinking-2507:qwen3-4b-thinking-2507-mlx")
    chat = lms.Chat(coach_mike)
    tool_list = [analyze_workout, meal_rec, recovery]

    print("\n" + "=" * 50)

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in ['q', 'quit', 'exit', 'done']:
                print("💪 Great chatting with you! Keep crushing those workouts!")
                break

            if not user_input:
                continue

            chat.add_user_message(user_input)
            print("\nCoach Mike: ", end="", flush=True)

            # Clear buffer for new response
            response_buffer = []

            # Run the model and collect response
            model.act(
                chat,
                tool_list,
                on_message=chat.append,
                on_prediction_fragment=collect_fragment,
            )

            # Filter out thinking tags and print the clean response
            full_response = ''.join(response_buffer)
            filtered_response = re.sub(r'<think>.*?</think>', '', full_response, flags=re.DOTALL).strip()

            if filtered_response:
                print(filtered_response, end="", flush=True)

        except KeyboardInterrupt:
            print("\n\n👋 Thanks for the great session!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("💭 Try asking a different question about your workout.")



if __name__ == "__main__":
    chat_loop()


