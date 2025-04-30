document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('revenueChart').getContext('2d');

    const labels = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    
    //lastest plugin line for each point data 
    const customPlugin= {
        id: 'customLine',
        beforeDraw(chart) {
            const ctx = chart.ctx;
            const chartArea = chart.chartArea; // Chart area boundaries
            const meta = chart.getDatasetMeta(0); // Get metadata for the first dataset
            const activePoint = chart.tooltip?.dataPoints?.[0]; // Get the active tooltip point (if any)

            if (chartArea && meta) {
                ctx.save();
                ctx.lineWidth = 1;
                // ctx.strokeStyle = '#5790FF'; // Vertical line color

                // Loop through all data points
                meta.data.forEach(point => {
                    const x = point.x; // X-coordinate of the data point
                    const y = point.y; // Y-coordinate of the data point

                    if (activePoint && activePoint.element.x === x) {
                        ctx.strokeStyle = '#0066ff'; // Highlight color when hovering
                    } else {
                        ctx.strokeStyle = '#a6c4ff'; // Default line color
                    }

                    ctx.beginPath();
                    ctx.moveTo(x, chartArea.bottom); // Start at the bottom of the chart
                    ctx.lineTo(x, y); // End at the data point
                    ctx.stroke();
                });

                ctx.restore();
            }
        },
        afterEvent(chart, args) {
            const event = args.event;
            const chartArea = chart.chartArea;
            const meta = chart.getDatasetMeta(0); // Get metadata for the first dataset
    
            if (!chartArea || !meta) return;
    
            // Check if the mouse is near any vertical line
            const mouseX = event.x;
            const mouseY = event.y;
    
            let foundPoint = null;
    
            meta.data.forEach(point => {
                const x = point.x; // X-coordinate of the data point
                const y = point.y; // Y-coordinate of the data point
    
                // Check if the mouse is near the vertical line
                if (mouseX >= x - 5 && mouseX <= x + 5 && mouseY >= chartArea.top && mouseY <= chartArea.bottom) {
                    foundPoint = point;
                }
            });
    
            if (foundPoint) {
                // Programmatically set the active elements and show the tooltip
                chart.setActiveElements([
                    { datasetIndex: 0, index: meta.data.indexOf(foundPoint) }
                ]);
                chart.tooltip.setActiveElements([
                    { datasetIndex: 0, index: meta.data.indexOf(foundPoint) }
                ], { x: foundPoint.x, y: foundPoint.y });
    
                chart.update();
            } else {
                // Clear active elements if no point is found
                chart.setActiveElements([]);
                chart.tooltip.setActiveElements([], { x: 0, y: 0 });
                chart.update();
            }
        }
    }

    //custom plugin first draft
    // const customPlugin = {
    //     id: 'customLine',
    //     beforeDraw(chart) {
    //         const ctx = chart.ctx;
    //         const activePoint = chart.tooltip?.dataPoints?.[0]; // Get the active tooltip point
    //         if (activePoint) {
    //             const x = activePoint.element.x; // X-coordinate of the active point
    //             const y = activePoint.element.y;
    //             const chartArea = chart.chartArea; // Chart area boundaries

    //             if (chartArea) {
    //                 ctx.save();
    //                 ctx.beginPath();
    //                 ctx.moveTo(x, chartArea.bottom); // Start at the bottom of the chart
    //                 ctx.lineTo(x, y); // End at the data point
    //                 ctx.lineWidth = 1;
    //                 ctx.strokeStyle = '#0066ff'; // Vertical line color
    //                 ctx.stroke();
    //                 ctx.restore();
    //             }
    //         }
    //     }
    // };
    
    const revenueData =  [
        280000, 290000, 300000, 320000, 330000, 340000, 350000, 340000, 310000, 400000, 375000, 390000
    ];

    const percentageChange = [
        0, 3.57, 3.45, 6.67, 3.13, 3.03, 2.94, -2.86, -8.82, 29.03, -6.25, 4.00
    ];

    const data = {
        labels: labels,
        datasets: [{
            label: 'Revenue',
            data:revenueData,
            borderColor: '#5790FF',
            borderWidth: 2,
            tension: 0.1, // Smooth curve
            fill: true,
            backgroundColor: 'rgba(0, 102, 255, 0.1)', // Light blue fill
            pointRadius: 1.5, // Highlight points
            pointHoverRadius: 4,
            pointBackgroundColor: '#5790FF',
            pointHoverBackgroundColor: '#ffffff',
            pointHoverBorderColor: '#0066ff',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 0,
        }]
    };

    const config = {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: {
                        display: false // Hide vertical grid lines
                    },
                    ticks: {
                        color: '#737373', // Secondary text color
                        font: {
                            size: 12
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#f5f5f5', // Light grid lines
                        lineWidth:0.3
                    },
                    ticks: {
                        color: '#737373', // Secondary text color
                        font: {
                            size: 12
                        },
                        callback: function (value) {
                            return value >= 1000 ? value / 1000 + 'k' : value; // Format y-axis values
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    backgroundColor: '#ffffff', // White background
                    titleColor: '#171717', // Black title text
                    bodyColor: '#171717', // Grey body text
                    borderColor: '#e0e0e0', // Light grey border
                    borderWidth: 1, // Border width
                    titleFont: {
                        size: 16, // Title font size
                        weight: '400' // Title font weight
                    },
                    bodyFont: {
                        size: 18, // Body font size
                        weight: '600'
                    },
                    padding: 15 , // Padding inside the tooltip
                    displayColors: false, // Hide the colored box next to the label
                    
                    callbacks: {
                        label: function (context) {
                            const index = context.dataIndex; // Get the index of the current data point
                            const revenue = revenueData[index].toLocaleString(); // Format revenue
                            const change = percentageChange[index].toFixed(2); // Format percentage change
                            return `$${revenue} (${change}%)`; // Combine revenue and percentage change    
                        },
                    }
                },
                legend: {
                    display: false // Hide legend
                },
            },
            elements: {
                line: {
                    borderJoinStyle: 'round' // Smooth line joins
                }
            }
        },
        plugins: [customPlugin] // Register the custom plugin
    };

    new Chart(ctx, config);
});