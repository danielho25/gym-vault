import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Success_Toast } from "../Toasts/Success_Toast";

const Workout_Form = () => {
  // setup date values
  // function getDate() {
  //   const current_date = new Date();
  //   const yyyy = current_date.getFullYear();
  //   const mm = current_date.getMonth();
  //   const dd = current_date.getDate();
  //   current_date = `${yyyy}-${mm}-${dd}`;

  //   return current_date
  // }
  

  const [formData, setFormData] = useState({
    exercise_name: "",
    sets: "",
    reps: "",
    // date: getDate()
  })

  const [errors, setErrors] = useState({});


  // handle form submission
  const handleSubmit = async (e) => {
    // prevent reloading the page
    e.preventDefault();
    const ValidationError = validateForm(formData);
    setErrors(ValidationError);

    if (Object.keys(ValidationError).length === 0) {
      try {
        const transformedData = {
          exercise_name: formData.exercise_name,
          sets: parseInt(formData.sets),
          reps: parseInt(formData.reps)
        };
  
        const response = await fetch('http://localhost:8000/workout_data', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(transformedData)
        })
  
        if (!response.ok) {
          throw new Error("'HTTP Error! status ${response.status}");
        }
  
        console.log("succesfully submitted", result)
        
        // toast shows up on loading
        setShowSuccessToast(true);
        setFormData({
          exercise_name: "",
          sets: "",
          reps: ""
        });
        // toast shows for certain amount of time
        setTimeout(() => {
          // Todo: implement fucntion to show toast!
          setShowSuccessToast(false);        
        }, 2000);
      }
      catch (error) {
        console.log("Error: error submitting workout: ", error);
        alert('Error submitting wokrout: ', {error});
      }
    }
  }
  const [showSuccessToast, setShowSuccessToast] = useState(false);

  // handle validation errors
  const validateForm = (data) => {
    let errors = {}

    if(!data.exercise_name) {
      errors.exercise_name = "Exercise name is required!"
    }
    if(!data.sets) {
      errors.sets = "please input how many sets you did!"
    }
    if(!data.reps) {
      errors.reps = "please input how many reps you did!"
    }
    // if(!data.date) {
    //   errors.exercise_name = "please input a date"
    // }

    return errors;
  }

  const handleChange = (e) => {
    const {name,value} = e.target;
    setFormData({...formData, [name]:value})
  }

  // TODO: Fix Toast, does not appear when submitting
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
                className="text-[#343A40] flex-[2] p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {errors.exercise_name && <span className="text-sm text-[#D77A61]">{errors.exercise_name}</span>}
            </div>
            
            <div className="flex flex-col">
              <input
                name="sets"
                type="number"
                placeholder="Sets"
                value={formData.sets}
                onChange={handleChange}
                className="text-[#343A40] flex-1 p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {errors.sets && <span className="text-sm text-[#D77A61]">{errors.sets}</span>}
            </div>
            
            <div className="flex flex-col">
              <input
                name="reps"
                type="number"
                placeholder="Reps"
                value={formData.reps}
                onChange={handleChange}
                className="text-[#343A40] flex-1 p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            {errors.reps && <span className="text-sm text-[#D77A61]">{errors.reps}</span>}
            </div>
            
          </div>

        <button
          type="button"
          // onClick={addExerciseRow}
          className="w-full py-2 text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition"
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
            // onClick={handleSubmit}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Submit Workout
          </button>
        </div>
      </form>
    </div>
    {showSuccessToast && <Success_Toast />}
    </>
  );
};

export default Workout_Form;