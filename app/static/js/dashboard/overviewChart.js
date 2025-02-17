function createChart(canvasId, url, chartType, chartTitle) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) {
    console.error(`Canvas ${canvasId} not found`);
    return;
  }

  fetch(url)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      if (!data.labels || !data.data) {
        console.error('Invalid data format received');
        return;
      }

      const config = {
          type: chartType,
          data: {
            labels: data.labels,
            datasets: [{
              label: chartTitle,
              data: data.data,
              borderColor: chartType === 'pie' ? undefined : '#039752',
              backgroundColor: chartType === 'pie' ? 
                ['#039752', '#04703E', '#034926', '#023319', '#01231C', '#011D13', '#00110B', '#000502', '#112110', '#223321'] :
                chartType === 'bar' ? '#039752' : undefined,
              tension: 0.1
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              title: {
                display: false,
                text: chartTitle
              },
              legend: {
                display: chartType === 'line' ? false : true
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    let label = context.label || '';
                    if (chartType === 'pie') {
                      return `${label}: ${Math.round(context.raw)}`;
                    } else {
                      if (label) {
                        label += ': ';
                      }
                      return label + Math.round(context.raw);
                    }
                  }
                }
              },
            }
          }
        };

      // Scales configuration only for bar and line charts
      if (chartType !== 'pie') {
        config.options.scales = {
          y: {
            beginAtZero: true,
            ticks: {
              precision: 0
            }
          }
        };
      }

      new Chart(canvas, config);
    })
    .catch(error => {
      console.error('Error loading chart data:', error);
      canvas.style.display = 'none';
      const errorDiv = document.createElement('div');
      errorDiv.className = 'chart-error';
      errorDiv.textContent = 'Unable to load chart data';
      canvas.parentNode.appendChild(errorDiv);
    });
}

// Initialize charts based on user role
function initializeCharts(roleId) {
  if (roleId === 1) {
    createChart('tradeFrequencyChart', '/dashboard/api/customer/trade-frequency', 'line', 'Trade-ins');
    createChart('buyingTrendChart', '/dashboard/api/customer/buying-trend', 'line', 'Orders');
    createChart('topCategoriesChart', '/dashboard/api/customer/top-categories', 'pie', 'Purchase Categories');
  } else if (roleId === 2 || roleId === 3) {
    createChart('weeklySignupsChart', '/dashboard/api/admin/monthly-signups', 'line', 'Weekly Sign-ups');
    createChart('categorySalesChart', '/dashboard/api/admin/category-sales', 'pie', 'Sales by Category');
    createChart('productSalesChart', '/dashboard/api/admin/product-sales', 'line', 'Monthly Sales');
  }
}

// Export the initialization function
window.initDashboardCharts = initializeCharts;