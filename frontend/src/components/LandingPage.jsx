import React from 'react';
import hero_img from '../img/sample_img.jpg'

const HeroSection = () => {
  return (
    <div className="h-screen flex flex-col justify-center w-screen bg-[#F8F9FA] mx-auto px-4 sm:px-6 lg:px-8">
      {/* Grid */}
      <div className="flex flex-col grid md:grid-cols-2 gap-4 md:gap-8 xl:gap-20 md:items-center">
        <div>
          <h1 className="block text-3xl font-bold text-[#343A40] sm:text-4xl lg:text-6xl lg:leading-tight">
            Start your journey with <span className="text-[#4C8DAE]">Sculpt.ai</span>
          </h1>
          <p className="mt-3 text-lg text-[#343A40]">
            The premiere fitness dashboard and coaching app.
          </p>

          {/* Buttons */}
          <div className="mt-7 grid gap-3 w-full sm:inline-flex">
            <a 
              className="py-3 px-4 inline-flex justify-center items-center gap-x-2 text-sm font-medium rounded-lg border border-[#343A40] bg-[#F8F9FA] text-[#F8F9FA] hover:bg-[#343A40] focus:outline-none focus:bg-[#3a7496] disabled:opacity-50 disabled:pointer-events-none transition-colors duration-200" 
              href="#"
            >
              Get started
              <svg className="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="m9 18 6-6-6-6"/>
              </svg>
            </a>
            <a 
              className="py-3 px-4 inline-flex justify-center items-center gap-x-2 text-sm font-medium rounded-lg border border-[#343A40] bg-[#F8F9FA] text-[#F8F9FA] hover:bg-[#343A40] shadow-sm hover:bg-[#E9E4D4] focus:outline-none focus:bg-[#E9E4D4] disabled:opacity-50 disabled:pointer-events-none transition-colors duration-200" 
              href="#"
            >
              Contact sales team
            </a>
          </div>
          {/* End Buttons */}          
        </div>
        {/* End Col */}

        <div className="relative ms-4">
          <img 
            className="h-auto max-w-xl rounded-lg shadow-xl dark:shadow-gray-800"
            src={hero_img} 
            alt="Hero Image"
          />
        </div>
        {/* End Col */}
      </div>
      {/* End Grid */}
    </div>
  );
};

export default HeroSection;