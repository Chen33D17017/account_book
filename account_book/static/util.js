/*
// from Chart.js
charType={
     type: 'bar',
     chartLabelDisplay: false
}

charData={
     data: ,
     labels: ,
}

With colorSchema and colorScale, please see https://github.com/d3/d3-scale-chromatic/blob/v1.5.0/README.md#schemePastel1
colorScale with interpolate methods
colorSchema with scheme methods
staticColorChart(chartType, chartId, chartData, colorSchema)

dynamicColorChart(chartType, chartId, chartData, colorScale, colorRangeInfo=[])

*/


function calculatePoint(i, intervalSize, colorRangeInfo) {
          var { colorStart, colorEnd, useEndAsStart } = colorRangeInfo;
          return (useEndAsStart
            ? (colorEnd - (i * intervalSize))
            : (colorStart + (i * intervalSize)));
        }

 function interpolateColors(dataLength, colorScale, colorRangeInfo) {
          var { colorStart, colorEnd } = colorRangeInfo;
          var colorRange = colorEnd - colorStart;
          var intervalSize = colorRange / dataLength;
          var i, colorPoint;
          var colorArray = [];
        
          for (i = 0; i < dataLength; i++) {
            colorPoint = calculatePoint(i, intervalSize, colorRangeInfo);
            colorArray.push(colorScale(colorPoint));
          }
        
          return colorArray;
        }

function createChart(chartType, chartData, chartId, COLORS){
    const chartElement = document.getElementById(chartId);
    const myChart = new Chart(chartElement, {
    type: chartType.type,
    data: {
      labels: chartData.labels,
      datasets: [
        {
          backgroundColor: COLORS,
          // hoverBackgroundColor: COLORS,
          data: chartData.data
        }
      ],
    },
    options: {
      responsive: true,
      legend: {
        display: chartType.chartLabelDisplay,
      },
      hover: {
        onHover: function(e) {
          var point = this.getElementAtEvent(e);
          e.target.style.cursor = point.length ? 'pointer' : 'default';
        },
      },
    }
  });

  return myChart;
}

function dynamicColorChart(chartType, chartId, chartData, colorScale, colorRangeInfo=[]) {
  if(colorRangeInfo){
    colorRangeInfo = {
      colorStart: 0,
      colorEnd: 1,
      useEndAsStart: true,
    };
  }
  
  const dataLength = chartData.data.length;
  /* Create color array */
  var COLORS = interpolateColors(dataLength, colorScale, colorRangeInfo);

  /* Create chart */
  return createChart(chartType, chartData, chartId, COLORS);
}

function staticColorChart(chartType, chartId, chartData, colorSchema) {
  
  const dataLength = chartData.data.length;
  /* Create color array */
  var COLORS = [];
  for(i=0; i<dataLength; i++){
    COLORS.push(colorSchema[i]);
  }
  // var COLORS = interpolateColors(dataLength, colorScale, colorRangeInfo);

  /* Create chart */
  return createChart(chartType, chartData, chartId, COLORS);
}
