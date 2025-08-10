import React, { useState, useEffect } from 'react';
import ReactApexChart from 'react-apexcharts';

const Macro_Chart = ({ 
  data = [70, 18, 12], 
  labels = ['Direct', 'Organic search', 'Referral'],
  legendLabels = ['Income', 'Outcome', 'Others']
}) => {

  const getChartOptions = () => {
    return {
      chart: {
        height: '100%',
        type: 'pie',
        zoom: {
          enabled: false
        }
      },
      series: data,
      labels: labels,
      title: {
        show: false
      },
      dataLabels: {
        style: {
          fontSize: '20px',
          fontFamily: 'Inter, ui-sans-serif',
          fontWeight: '400',
          colors: ['#fff', '#fff', isDarkMode ? '#fff' : '#1f2937']
        },
        dropShadow: {
          enabled: false
        },
        formatter: (value) => `${value.toFixed(1)}%`
      },
      plotOptions: {
        pie: {
          dataLabels: {
            offset: -15
          }
        }
      },
      legend: {
        show: false // We're using our custom legend
      },
      stroke: {
        width: 4,
        colors: [isDarkMode ? 'rgb(38, 38, 38)' : 'rgb(255, 255, 255)']
      },
      grid: {
        padding: {
          top: -10,
          bottom: -14,
          left: -9,
          right: -9
        }
      },
      tooltip: {
        enabled: false
      },
      states: {
        hover: {
          filter: {
            type: 'none'
          }
        }
      },
      // Step 3: Theme-aware colors
      colors: isDarkMode 
        ? ['#3b82f6', '#22d3ee', '#404040'] 
        : ['#3b82f6', '#22d3ee', '#e5e7eb']
    };
  };

  // Step 4: Define legend colors that match the chart
  const getLegendColors = () => {
    return isDarkMode 
      ? ['bg-blue-600', 'bg-cyan-500', 'bg-neutral-700'] 
      : ['bg-blue-600', 'bg-cyan-500', 'bg-gray-300'];
  };

  const legendColors = getLegendColors();

  return (
    <div className="p-4">
      <div className="h-75 flex flex-col justify-center items-center">
        {/* Step 5: The actual chart */}
        <div style={{ height: '300px', width: '100%' }}>
          <ReactApexChart
            options={getChartOptions()}
            series={data}
            type="pie"
            height="100%"
          />
        </div>
        
        {/* Step 6: Custom Legend */}
        <div className="flex justify-center sm:justify-end items-center gap-x-4 mt-3 sm:mt-6">
          {legendLabels.map((label, index) => (
            <div key={index} className="inline-flex items-center">
              <span className={`size-2.5 inline-block ${legendColors[index]} rounded-sm me-2`}></span>
              <span className="text-[13px] text-gray-600 dark:text-neutral-400">
                {label}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Macro_Chart;