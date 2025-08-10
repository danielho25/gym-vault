import React from 'react'
import Sidebar_Slide from './Sidebar_Slide';
import Dashboard_Only from './Dashboard_Only';

const MainDashboard = () => {
  return (
    <main className="mt-20 grid gap-4 p-4 grid-cols-1 lg:grid-cols-[280px,_1fr] bg-[#E9E4D4] min-h-screen w-screen">
      <div className='flex flex-row pt-6'>
        <Sidebar_Slide />
        <Dashboard_Only />
      </div>

    </main>
  );
};

export default MainDashboard;