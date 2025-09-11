import os
import psycopg
from fastapi import FastAPI, HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
from fastapi.testclient import TestClient
from dotenv import load_dotenv
# from datetime import date

# API to set workout data in postgres

# model to define the input of our workout data
class Workout_Data(BaseModel):
    exercise_name: str
    sets: int
    reps: int
    # date: date = Field(default_factory=date.today())


class Workout_Data_Row(BaseModel):
    workouts: List[Workout_Data]


# create an instance of the api
app = FastAPI()

# CORS origins - be more specific in production
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",  # Common React dev port
    "http://127.0.0.1:3000",
]

# Add CORS middleware BEFORE other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Use specific origins instead of "*" for better security
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Debug middleware - place AFTER CORS
@app.middleware("http")
async def log_origin(request, call_next):
    print(">>> REQUEST METHOD:", request.method)
    print(">>> ORIGIN HEADER:", request.headers.get("origin"))
    print(">>> CONTENT-TYPE:", request.headers.get("content-type"))
    response = await call_next(request)
    print(">>> RESPONSE STATUS:", response.status_code)
    return response


# Database connection helper
def get_db_connection():
    try:
        conn = psycopg.connect(os.getenv("DATABASE_URL"))
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")


# POST endpoint to create new workout data
@app.post("/workout_data", response_model=Workout_Data)
def create_workout_data(workout_data: Workout_Data):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fixed: Remove extra %s placeholder - only 3 values being inserted
        cursor.execute(
            """
            INSERT INTO workout_data (exercise_name, sets, reps)
            VALUES (%s, %s, %s);
            """,
            (workout_data.exercise_name, workout_data.sets, workout_data.reps)
        )

        conn.commit()
        cursor.close()
        return workout_data

    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error inserting data: {str(e)}")
    finally:
        if conn:
            conn.close()


# GET endpoint to retrieve all workout data
@app.get("/workout_data", response_model=List[Workout_Data])
def get_all_workout_data():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT exercise_name, sets, reps FROM workout_data")
        results = cursor.fetchall()

        cursor.close()

        # Convert results to list of Workout_Data objects
        workout_list = []
        for row in results:
            workout_list.append(Workout_Data(
                exercise_name=row[0],
                sets=row[1],
                reps=row[2],
                # date=row[3]
            ))

        return workout_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
    finally:
        if conn:
            conn.close()


# GET endpoint to retrieve workout data by exercise name
@app.get("/workout_data/{exercise_name}", response_model=List[Workout_Data])
def get_workout_by_exercise(exercise_name: str):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT exercise_name, sets, reps FROM workout_data WHERE exercise_name = %s",
            (exercise_name,)
        )
        results = cursor.fetchall()

        cursor.close()

        if not results:
            raise HTTPException(status_code=404, detail=f"No workout data found for exercise: {exercise_name}")

        # Convert results to list of Workout_Data objects
        workout_list = []
        for row in results:
            workout_list.append(Workout_Data(
                exercise_name=row[0],
                sets=row[1],
                reps=row[2],
                # date=row[3]
            ))

        return workout_list

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
    finally:
        if conn:
            conn.close()


# DELETE endpoint to remove workout data
@app.delete("/workout_data/{exercise_name}")
def delete_workout_by_exercise(exercise_name: str):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the exercise exists
        cursor.execute("SELECT COUNT(*) FROM workout_data WHERE exercise_name = %s", (exercise_name,))
        count = cursor.fetchone()[0]

        if count == 0:
            raise HTTPException(status_code=404, detail=f"No workout data found for exercise: {exercise_name}")

        # Delete the exercise data
        cursor.execute("DELETE FROM workout_data WHERE exercise_name = %s", (exercise_name,))
        conn.commit()
        cursor.close()

        return {"message": f"Successfully deleted {count} workout entries for exercise: {exercise_name}"}

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting data: {str(e)}")
    finally:
        if conn:
            conn.close()


# Add a health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    load_dotenv()
    main()