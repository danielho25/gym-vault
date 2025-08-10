import { useState } from 'react';
import { Link } from 'react-router-dom';

export default function Register_Form() {
    // create state to store the form data
    // these forms provide memory for the user inputs
    const [lastName, setLastName] = useState('');
    const [firstName, setFirstName] = useState('');
    const [age, setAge] = useState('');
    const [email, setEmail] = useState('');
    const [terms, setTerms] = useState(false);
    const [password, setPassword] = useState('');
    const [submittedData, setSubmittedData] = useState(null);

    // handle form submission when user clicks 'submit'
    const handleSubmit = (e) => {
        // prevent reloading the page
        e.preventDefault();

        // Basic validation
        if (!firstName || !lastName || !age || !email || !password || !terms) {
            alert('Please fill in all fields and accept the terms');
            return;
        }

        // handle the form data
        const formData = {
            lastName: lastName,
            firstName: firstName,
            age: age,
            email: email,
            password: password,
            termsAccepted: terms,
            submissionTime: new Date().toLocaleString()
        };

        // store the submitted data to show user
        setSubmittedData(formData);

        // clear form
        setLastName('');
        setFirstName('');
        setAge('');
        setEmail('');
        setPassword('');
        setTerms(false);
    };

    // html form structure
    return (
        <div className=" bg-white h-screen flex flex-col w-screen min-h-screen justify-center items-center">
            <h1 className='text-[#343840]'>Register</h1>
            <div className="space-y-5">
                <div className="mb-5">
                    <label htmlFor="lastName" className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        Last Name
                    </label>
                    <input 
                        type="text" 
                        id="lastName" 
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                        className="shadow-xs bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-xs-light" 
                        placeholder="Enter your last name" 
                        required 
                    />
                </div>
                
                <div className="mb-5">
                    <label htmlFor="firstName" className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        First Name
                    </label>
                    <input 
                        type="text" 
                        id="firstName" 
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                        className="shadow-xs bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-xs-light" 
                        placeholder="Enter your first name" 
                        required 
                    />
                </div>
                
                <div className="mb-5">
                    <label htmlFor="age" className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        Age
                    </label>
                    <input 
                        type="number" 
                        id="age" 
                        value={age}
                        onChange={(e) => setAge(e.target.value)}
                        className="shadow-xs bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-xs-light" 
                        placeholder="Enter your age"
                        required 
                    />
                </div>
                
                <div className="mb-5">
                    <label htmlFor="email" className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        Email
                    </label>
                    <input 
                        type="email" 
                        id="email" 
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="shadow-xs bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-xs-light" 
                        placeholder="name@example.com"
                        required 
                    />
                </div>

                <div className="mb-5">
                    <label htmlFor="password" className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        Password
                    </label>
                    <input 
                        type="password" 
                        id="password" 
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="shadow-xs bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-xs-light" 
                        placeholder="Enter your password"
                        required 
                    />
                </div>
                
                <div className="flex items-start mb-5">
                    <div className="flex items-center h-5">
                        <input 
                            id="terms" 
                            type="checkbox" 
                            checked={terms}
                            onChange={(e) => setTerms(e.target.checked)}
                            className="w-4 h-4 border border-gray-300 rounded-sm bg-gray-50 focus:ring-3 focus:ring-blue-300 dark:bg-gray-700 dark:border-gray-600 dark:focus:ring-blue-600 dark:ring-offset-gray-800 dark:focus:ring-offset-gray-800" 
                            required 
                        />
                    </div>
                    <label htmlFor="terms" className="ms-2 text-sm font-medium text-gray-900 dark:text-gray-300">
                        I agree with the <a href="#" className="text-blue-600 hover:underline dark:text-blue-500">terms and conditions</a>
                    </label>
                </div>
                
                <button 
                    onClick={handleSubmit}
                    className="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
                >
                    Register new account
                </button>

                <Link to={"/"}>
                    <button className="ml-3 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
                        Return to Home
                    </button> 
                </Link>
                
                    
            </div>

            {/* Show submitted data (for demonstration) */}
            {submittedData && (
                <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
                    <h3 className="text-lg font-semibold text-green-800 mb-2">Registration Successful!</h3>
                    <div className="text-sm text-green-700">
                        <p><strong>Name:</strong> {submittedData.firstName} {submittedData.lastName}</p>
                        <p><strong>Age:</strong> {submittedData.age}</p>
                        <p><strong>Email:</strong> {submittedData.email}</p>
                        <p><strong>Terms Accepted:</strong> {submittedData.termsAccepted ? 'Yes' : 'No'}</p>
                        <p><strong>Submitted:</strong> {submittedData.submissionTime}</p>
                    </div>
                </div>
            )}
        </div>
    );
}