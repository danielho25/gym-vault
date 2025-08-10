import React from 'react'
import Progress_Graph from './Graph_Carousel/Progress_Graph';
import { Link } from 'react-router-dom';
import Workout_Form from '../Forms/Workout_Form';

const Dashboard_Only = () => {
    return (
      <main className="min-h-screen bg-[#F9F6EE] p-7 w-screen flex flex-col">
        <div className="flex-1 max-w-7xl mx-auto w-full">
          {/* Header Section */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Dashboard</h1>
            <p className="text-gray-600">Welcome back! Here's what's happening.</p>
          </div>
          
          {/* Main content area with responsive grid */}
          <div className="flex-1">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* First Chart Card */}
              <div className="rounded-2xl border border-[#343A40] bg-[#F8F9FA] p-6 shadow-sm">
                <div className="mb-4">
                  <h3 className="text-lg font-semibold text-[#4C8DAE] mb-1">Performance Metrics</h3>
                  <p className="text-sm text-gray-600">Track your progress over time</p>
                </div>
                <Progress_Graph />
              </div>
              
              {/* Second Chart Card */}
              <div className="rounded-2xl border border-[#343A40] bg-[#F8F9FA] p-6 shadow-sm">
                <div className="mb-4">
                  <h3 className="text-lg font-semibold text-[#4C8DAE] mb-1">Analytics Overview</h3>
                  <p className="text-sm text-gray-600">Key insights and trends</p>
                </div>
                <Progress_Graph />
              </div>
            </div>
            
            {/* Additional Stats Section */}
            <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* first card */}
              <div className="bg-[#4C8DAE] rounded-xl w-full transform duration-500 hover:translate-x-1 hover:-translate-y-1 pointer-events-none">
                <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 transform duration-500 hover:-translate-x-2 hover:translate-y-2 pointer-events-auto">
                  <div className="flex items-center justify-between">
                    <Link to={"/Workout_Form"}>
                      <p className="text-l font-medium text-gray-600">Input a new workout here!</p>
                      <div className='text-gray-600'>put arrow here</div>
                    </Link>
                    <div className="text-green-500 text-2xl">👥</div>
                  </div>
                </div>
              </div>
              
              {/* second card */}
              <div className="bg-[#4C8DAE] rounded-xl w-full transform duration-500 hover:translate-x-1 hover:-translate-y-1 pointer-events-none">
                <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 transform duration-500 hover:-translate-x-2 hover:translate-y-2 pointer-events-auto">
                  <div className="flex items-center justify-between">
                    <Link to={"/Workout_Form"}>
                      <p className="text-l font-medium text-gray-600">Input new macro chart here!</p>
                      <div className='text-gray-600'>put arrow here</div>
                    </Link>
                    <div className="text-green-500 text-2xl">👥</div>
                  </div>
                </div>
              </div>

              {/* third card */}
              {/* <div className="bg-[#4C8DAE] rounded-xl w-full transform duration-500 hover:translate-x-1 hover:-translate-y-1 pointer-events-none">
                <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 transform duration-500 hover:-translate-x-2 hover:translate-y-2 pointer-events-auto">
                  <div className="flex items-center justify-between">
                    <Link to={"/Workout_Form"}>
                      <p className="text-l font-medium text-gray-600">Input a new workout</p>
                      <div className='text-gray-600'>put arrow here</div>
                    </Link>
                    <div className="text-green-500 text-2xl">👥</div>
                  </div>
                </div>
              </div> */}

            </div>
          </div>
        </div>

        <Link to={"/"} className='pt-5'>
          <button className='pt-5 flex items-center bg-[#4C8DAE] text-[#F8F9FA]'>Return To Home</button>
        </Link>
      </main>
    );
  };

export default Dashboard_Only;
