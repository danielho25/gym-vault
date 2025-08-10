import React from 'react'

const Sidebar_Slide = () => {
    const menuItems = [
      { name: 'Dashboard', icon: '📊' },
      { name: 'Analytics', icon: '📈' },
      { name: 'Reports', icon: '📋' },
      { name: 'Settings', icon: '⚙️' },
      { name: 'Profile', icon: '👤' },
    ];
  
    return (
      <div className="flex flex-col h-full">
        <div className="overflow-y-auto sticky top-4 h-[calc(100vh-32px-48px)] text-black bg-white rounded-lg shadow-sm border border-gray-200">
          {/* Sidebar Header */}
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-800">Menu</h2>
          </div>
          
          {/* Navigation Items */}
          <nav className="p-2">
            {menuItems.map((item, index) => (
              <a
                key={index}
                href="#"
                className="flex items-center gap-3 px-3 py-2 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors duration-200"
              >
                <span className="text-lg">{item.icon}</span>
                <span className="font-medium">{item.name}</span>
              </a>
            ))}
          </nav>

        </div>
  
        {/* Plan Toggle Section */}
        <div className="fixed sticky mt-4 p-4 bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <span className="fixed sticky text-sm font-medium text-gray-700">Pro Plan</span>
            <button className="fixed sticky px-3 py-1 bg-blue-500 text-white text-xs rounded-full hover:bg-blue-600 transition-colors">
              Upgrade
            </button>
          </div>
        </div>
      </div>
    );
  };

export default Sidebar_Slide;