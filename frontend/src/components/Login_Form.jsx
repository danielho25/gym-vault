import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';

const Login_Form= () => {
    // create state to store the form data
    // these forms provide memory for the user inputs
    const [formData, setFormData] = useState({
        email: "",
        password: ""
    });

    const [errors, setErrors] = useState({});

    const navigate = useNavigate();

    // handle form submission when user clicks 'submit'
    const handleSubmit = (e) => {
        // prevent reloading the page
        e.preventDefault();
        const ValidationError = validateForm(formData);
        setErrors(ValidationError);

        if (Object.keys(ValidationError).length === 0 ) {
            console.log("successfully submitted", formData)
            navigate('/Dashboard/MainDashboard')
        }
        
    };

    // hanlde validation error
    const validateForm = (data) => {
        let errors = {};

        if(!data.email) {
            errors.email = "email is required!"
        }
        if(!data.password) {
            errors.password = "password is required!"
        }
        
        return errors;
    }

    // this function is not being used
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email)
    }

    const handleChange = (e) => {
        const {name,value} = e.target;
        setFormData({...formData, [name]: value})
    }

    // html form structure
    // TODO: add validateEmail function into the form!
    return (
        <form onSubmit={handleSubmit}>
          <div className="bg-white h-screen flex flex-col w-screen min-h-screen justify-center items-center">
            <h1 className="text-[#343840]">Login</h1>
      
            <div className="space-y-5">
              {/* Email Field */}
              <div className="mb-5">
                <label
                  htmlFor="email"
                  className="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
                >
                  Email
                </label>
                <input
                  name="email"
                  type="email"
                  onChange={handleChange}
                  value={formData.email}
                  className="shadow-xs bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg 
                             focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 
                             dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white 
                             dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-xs-light"
                  placeholder="name@example.com"
                />
                {errors.email && (
                  <span className="text-sm text-[#D77A61]">{errors.email}</span>
                )}
              </div>
      
              {/* Password Field */}
              <div className="mb-5">
                <label
                  htmlFor="password"
                  className="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
                >
                  Password
                </label>
                <input
                  name="password"
                  type="password"
                  onChange={handleChange}
                  value={formData.password}
                  className="shadow-xs bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg 
                             focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 
                             dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white 
                             dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-xs-light"
                  placeholder="Enter your password"
                />
                {errors.password && (
                  <span className="text-sm text-[#D77A61]">{errors.password}</span>
                )}
              </div>
      
              {/* Navigation & Action Buttons */}
              <Link to="/register">
                <button
                  type="button"
                  className="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none 
                             focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center 
                             dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
                >
                  Not a user? Register new account here!
                </button>
              </Link>
      
              <Link to="/">
                <button
                  type="button"
                  className="ml-3 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none 
                             focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center 
                             dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
                >
                  Return to Home
                </button>
              </Link>
      
              <button
                type="submit"
                className="ml-3 text-[#343A40] bg-[#A3B18A] hover:bg-blue-800 focus:ring-4 focus:outline-none 
                           focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center 
                           dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
              >
                Login
              </button>
            </div>
          </div>
        </form>
      );
}      

export default Login_Form;
