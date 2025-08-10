import React from 'react'

export const Success_Toast = () => {
  return (
    <div id="toast-success" 
    className='fixed flex items-center w-full max-w-xs p-4 space-x-4 divide-x 
    rtl:divide-x-reverse divide-gray-200 rounded-lg shadow-sm top-5 right-5 bg-[#A3B18A] text-[#343A40]' role="alert">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
        </svg>
        <div className='text-sm font-italic'>Workout Successful!</div>
    </div>
  );
};