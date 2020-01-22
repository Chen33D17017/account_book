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

Chart.pluginService.register({
    beforeDraw: function (chart) {
	if (chart.config.options.elements.center && chart.config.options.elements.center.display) {
            //Get ctx from string
            var ctx = chart.chart.ctx;
            
	    //Get options from the center object in options
            var centerConfig = chart.config.options.elements.center;
      	    var fontStyle = centerConfig.fontStyle || 'Arial';
	    var txt = centerConfig.text;
            var color = centerConfig.color || '#000';
            var sidePadding = centerConfig.sidePadding || 20;
            var sidePaddingCalculated = (sidePadding/100) * (chart.innerRadius * 2)
            //Start with a base font of 30px
            ctx.font = "30px " + fontStyle;
            
	    //Get the width of the string and also the width of the element minus 10 to give it 5px side padding
            var stringWidth = ctx.measureText(txt).width;
            var elementWidth = (chart.innerRadius * 2) - sidePaddingCalculated;

            // Find out how much the font can grow in width.
            var widthRatio = elementWidth / stringWidth;
            var newFontSize = Math.floor(30 * widthRatio);
            var elementHeight = (chart.innerRadius * 2);

            // Pick a new font size so it will not be larger than the height of label.
            var fontSizeToUse = Math.min(newFontSize, elementHeight);

	    //Set font settings to draw it correctly.
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            var centerX = ((chart.chartArea.left + chart.chartArea.right) / 2);
            var centerY = ((chart.chartArea.top + chart.chartArea.bottom) / 2);
            ctx.font = fontSizeToUse+"px " + fontStyle;
            ctx.fillStyle = color;
            
            //Draw text in center
            ctx.fillText(txt, centerX, centerY);
	}
    }
});



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
	    onClick: function (e, el) {
		if (! el || el.length === 0) return;
		console.log('onClick : label ' + el[0]._model.label);
            },
	    onHover: function(e) {
		var point = this.getElementAtEvent(e);
		e.target.style.cursor = point.length ? 'pointer' : 'default';
	    },
	    elements: {
		center: {
		    text: chartData.centerText,
		    color: chartData.centerDisplayColor, // Default is #000000
		    fontStyle: 'Arial', // Default is Arial
		    sidePadding: 20, // Defualt is 20 (as a percentage)
		    display: chartData.centerDisplay,
		}
	    }
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
