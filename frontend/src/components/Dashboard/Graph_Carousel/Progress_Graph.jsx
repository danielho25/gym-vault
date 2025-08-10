import React, { useState } from 'react';
import Chart from 'react-apexcharts';

const Progress_Graph = () => {
  const [state, setState] = useState({
    series: [
      {
        name: 'Workouts',
        data: [45, 89, 33, 12, 49, 190, 20]
      },
      {
        name: 'Macros',
        data: [11, 45, 85, 23, 65, 67, 99]
      },
      {
        name: 'Sleep',
        data: [44, 66, 94, 125, 73, 24, 38]
      }
    ],
    options: {
      chart: {
        height: 350,
        type: 'area'
      },
      dataLabels: {
        enabled: false
      },
      stroke: {
        curve: 'smooth'
      },
      xaxis: {
        type: 'datetime',
        categories: [
          "2025-08-07T00:00:00.000Z", "2025-08-07T01:30:00.000Z", "2025-08-07T02:30:00.000Z", "2025-08-07T03:30:00.000Z", "2025-08-07T04:30:00.000Z", "2025-08-07T05:30:00.000Z", "2025-08-07T06:30:00.000Z"
        ]
      },
      tooltip: {
        x: {
          format: 'dd/MM/yy HH:mm'
        }
      }
    }
  });

  return (
    <div className='w-full'>
      <div id='chart' className='flex flex-col'>
        <Chart options={state.options} series={state.series} type="area" height={500} />
      </div>
    </div>
  );
};

export default Progress_Graph;
