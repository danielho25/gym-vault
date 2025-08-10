import React, { useState, useEffect } from 'react';
import ReactApexChart from 'react-apexcharts';

// const Sleep_Chart = ({ 
//   data = [23000, 44000, 55000, 57000, 56000, 61000, 58000, 63000, 60000, 66000, 34000, 78000],
//   categories = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
//   seriesName = 'Sales',
//   height = 300
// }) => {
//   const series = [
//     {
//       name: seriesName,
//       data: data
//     }
//   ];

// const getChartOptions = () => {
//   return {
//     chart: {
//       type: 'bar',
//         height: height,
//         toolbar: {
//           show: false
//         },
//         zoom: {
//           enabled: false
//         }
//       },
//       plotOptions: {
//         bar: {
//           horizontal: false,      // Vertical bars
//           columnWidth: '16px',    // Bar width
//           borderRadius: 0         // Square corners
//         }
//       },
//       legend: {
//         show: false  // No legend needed for single series
//       },
//       dataLabels: {
//         enabled: false  // Don't show values on top of bars
//       },
//       stroke: {
//         show: true,
//         width: 8,                    // Space between bars
//         colors: ['transparent']      // No border around bars
//       },
//       xaxis: {
//         categories: categories,
//         axisBorder: {
//           show: false
//         },
//         axisTicks: {
//           show: false
//         },
//         crosshairs: {
//           show: false
//         },
//         labels: {
//           style: {
//             colors: isDarkMode ? '#a3a3a3' : '#9ca3af',
//             fontSize: '13px',
//             fontFamily: 'Inter, ui-sans-serif',
//             fontWeight: 400
//           },
//           offsetX: -2,
//           formatter: (title) => title.slice(0, 3)  // "January" → "Jan"
//         }
//       },
//       yaxis: {
//         labels: {
//           align: 'left',
//           minWidth: 0,
//           maxWidth: 140,
//           style: {
//             colors: isDarkMode ? '#a3a3a3' : '#9ca3af',
//             fontSize: '13px',
//             fontFamily: 'Inter, ui-sans-serif',
//             fontWeight: 400
//           },
//           formatter: (value) => value >= 1000 ? `${value / 1000}k` : value
//         }
//       },
//       grid: {
//         borderColor: isDarkMode ? '#404040' : '#e5e7eb'
//       },
//       states: {
//         hover: {
//           filter: {
//             type: 'darken',
//             value: 0.9  // Darken bars on hover
//           }
//         }
//       },
//       tooltip: {
//         y: {
//           formatter: (value) => `$${value >= 1000 ? `${value / 1000}k` : value}`
//         }
//       },
//       // Step 4: Theme-aware colors
//       colors: isDarkMode ? ['#3b82f6'] : ['#2563eb'],
      
//       // Step 5: Responsive design
//       responsive: [{
//         breakpoint: 568,  // Mobile breakpoint
//         options: {
//           chart: {
//             height: height
//           },
//           plotOptions: {
//             bar: {
//               columnWidth: '14px'  // Slightly thinner bars on mobile
//             }
//           },
//           stroke: {
//             width: 8
//           },
//           xaxis: {
//             labels: {
//               style: {
//                 colors: isDarkMode ? '#a3a3a3' : '#9ca3af',
//                 fontSize: '11px',    // Smaller font on mobile
//                 fontFamily: 'Inter, ui-sans-serif',
//                 fontWeight: 400
//               },
//               offsetX: -2,
//               formatter: (title) => title.slice(0, 3)  // Keep abbreviation
//             }
//           },
//           yaxis: {
//             labels: {
//               align: 'left',
//               minWidth: 0,
//               maxWidth: 140,
//               style: {
//                 colors: isDarkMode ? '#a3a3a3' : '#9ca3af',
//                 fontSize: '11px',    // Smaller font on mobile
//                 fontFamily: 'Inter, ui-sans-serif',
//                 fontWeight: 400
//               },
//               formatter: (value) => value >= 1000 ? `${value / 1000}k` : value
//             }
//           }
//         }
//       }]
//     };
//   };

//   return (
//     <div className="w-full">
//       <ReactApexChart
//         options={getChartOptions()}
//         series={series}
//         type="bar"
//         height={height}
//       />
//     </div>
//   );
// };

export default Sleep_Chart;