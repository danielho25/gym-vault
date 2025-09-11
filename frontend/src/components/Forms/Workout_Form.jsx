import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Success_Toast } from "../Toasts/Success_Toast";
import {useDispatch} from 'react-redux'

// TODO: FIX CORS ERROR! LOGIC IS NOT WORKING

const Workout_Form = () => {
  const [formData, setFormData] = useState({
    exercise_name: "",
    sets: "",
    reps: "",
  })

  const [errors, setErrors] = useState({});
  const [showSuccessToast, setShowSuccessToast] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // handle form submission
  const handleSubmit = async (e) => {
    // prevent reloading the page
    e.preventDefault();
    const ValidationError = validateForm(formData);
    setErrors(ValidationError);

    if (Object.keys(ValidationError).length === 0) {
      setIsSubmitting(true);
      try {
        const transformedData = {
          exercise_name: formData.exercise_name,
          sets: parseInt(formData.sets),
          reps: parseInt(formData.reps)
        };

        console.log("Submitting data:", transformedData);
  
        const response = await fetch('http://localhost:8000/workout_data', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify(transformedData)
        });

        console.log("Response status:", response.status);
        console.log("Response ok:", response.ok);
  
        if (!response.ok) {
          const errorData = await response.text();
          console.error("Error response:", errorData);
          throw new Error(`HTTP Error! status ${response.status}: ${errorData}`);
        }

        // Parse the response
        const result = await response.json();
        console.log("Successfully submitted:", result);
        
        // Reset form and show success toast
        setFormData({
          exercise_name: "",
          sets: "",
          reps: ""
        });
        
        // Show toast
        setShowSuccessToast(true);
        setTimeout(() => {
          setShowSuccessToast(false);        
        }, 2000);

      } catch (error) {
        console.error("Error submitting workout:", error);
        alert(`Error submitting workout: ${error.message}`);
      } finally {
        setIsSubmitting(false);
      }
    }
  }

  // handle validation errors
  const validateForm = (data) => {
    let errors = {}

    if(!data.exercise_name.trim()) {
      errors.exercise_name = "Exercise name is required!"
    }
    if(!data.sets || parseInt(data.sets) <= 0) {
      errors.sets = "Please input a valid number of sets!"
    }
    if(!data.reps || parseInt(data.reps) <= 0) {
      errors.reps = "Please input a valid number of reps!"
    }

    return errors;
  }

  const handleChange = (e) => {
    const {name, value} = e.target;
    setFormData({...formData, [name]: value});
    
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors({...errors, [name]: ""});
    }
  }

  return (
    <>
      <div className="max-w-3xl mx-auto p-6 bg-white rounded-2xl shadow-md">
        <h1 className="text-l font-bold text-gray-800 mb-4">Input a new workout!</h1>
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="flex gap-2">

            <div className="flex flex-col">
              <input
                name="exercise_name"
                type="text"
                placeholder="Exercise Name"
                value={formData.exercise_name}
                onChange={handleChange}
                disabled={isSubmitting}
                className="text-[#343A40] flex-[2] p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              />
              {errors.exercise_name && <span className="text-sm text-[#D77A61]">{errors.exercise_name}</span>}
            </div>
            
            <div className="flex flex-col">
              <input
                name="sets"
                type="number"
                placeholder="Sets"
                min="1"
                value={formData.sets}
                onChange={handleChange}
                disabled={isSubmitting}
                className="text-[#343A40] flex-1 p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              />
              {errors.sets && <span className="text-sm text-[#D77A61]">{errors.sets}</span>}
            </div>
            
            <div className="flex flex-col">
              <input
                name="reps"
                type="number"
                placeholder="Reps"
                min="1"
                value={formData.reps}
                onChange={handleChange}
                disabled={isSubmitting}
                className="text-[#343A40] flex-1 p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              />
              {errors.reps && <span className="text-sm text-[#D77A61]">{errors.reps}</span>}
            </div>
            
          </div>

          <button
            type="button"
            // onClick={addExerciseRow}
            disabled={isSubmitting}
            className="w-full py-2 text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            + Add Exercise
          </button>

          <div className="flex justify-between mt-6">
            <Link
              to=""
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition"
            >
              Return Home
            </Link>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? "Submitting..." : "Submit Workout"}
            </button>
          </div>
        </form>
      </div>
      {showSuccessToast && <Success_Toast />}
    </>
  );
};

export default Workout_Form;