function createAccountDetailsChart(canvasId, url, chartType, chartTitle) {
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
              ['#039752', '#04703E', '#034926', '#023319'] :
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
            }
          }
        }
      };

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

function initializeAccountDetailsCharts(userId) {
  // Order Trend Chart
  createAccountDetailsChart('userOrderTrendChart', `/dashboard/api/customer/order-trend/${userId}`, 'line', 'Order Trend');
  
  // Voucher Types Chart
  createAccountDetailsChart('userVoucherTypesChart', `/dashboard/api/customer/voucher-types/${userId}`, 'pie', 'Voucher Types');
  
  // Review Trend Chart
  createAccountDetailsChart('userReviewTrendChart', `/dashboard/api/customer/review-trend/${userId}`, 'line', 'Review Trend');
}

// Export the initialization function
window.initAccountDetailsCharts = initializeAccountDetailsCharts;