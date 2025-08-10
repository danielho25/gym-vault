import React from 'react';
import { Link } from 'react-router-dom';


const Header = () => {
  return (
    <>
      {/* Header */}
      <header className="w-full bg-[#F8F9FA] shadow-sm fixed top-0 left-0 right-0 z-50">
        <div className="flex items-center justify-between px-6 py-4 max-w-none min-h-[80px]">
          {/* Logo */}
          <div className="flex items-center flex-shrink-0">
            <div className="w-8 h-8 bg-sky-400 rounded-full flex items-center justify-center mr-3">
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
            </div>
            <h1 className="text-s md:text-3xl lg:text-4xl font-extrabold pl-5">
              <span className="text-transparent bg-clip-text bg-gradient-to-r to-[#4C8DAE] from-sky-400">Sculpt.ai</span>
            </h1>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-12 flex-1 justify-center">
            <Link to="/notfoundpage" className="text-[#4C8DAE] hover:text-[#3A6B8E] font-medium transition-colors">About</Link>
            <Link to="/notfoundpage" className="text-[#4C8DAE] hover:text-[#3A6B8E] font-medium transition-colors">Team</Link>
            <Link to="/notfoundpage" className="text-[#4C8DAE] hover:text-[#3A6B8E] font-medium transition-colors">Services</Link>
            <Link to="/notfoundpage" className="text-[#4C8DAE] hover:text-[#3A6B8E] font-medium transition-colors">Blog</Link>
          </nav>

          {/* Login/Register Buttons */}
          <div className="flex items-center space-x-4 flex-shrink-0">
            <Link to="/Login" className="bg-[#F8F9FA] text-[#4C8DAE] border border-[#4C8DAE] px-6 py-2 rounded-md hover:bg-[#DDE2E6] transition-colors">
              Login
            </Link>
            <Link to="/register" className="text-[#4C8DAE] border border-[#4C8DAE] px-6 py-2 rounded-md hover:bg-[#E9E4D4] transition-colors">
              Register
            </Link>
          </div>

          {/* Mobile menu button */}
          <button className="md:hidden text-gray-600 ml-4">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </header>
    </>
  );
};

export default Header;