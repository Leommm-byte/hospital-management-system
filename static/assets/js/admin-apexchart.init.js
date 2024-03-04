

//=========================================//
/*/*         Apexcharts for admin          */
//=========================================//

console.log(maleCounts, femaleCounts);

try {
    var options1 = {
        series: [{
            name: 'Male',
            data: maleCounts.map(entry => entry[1])  // entry[1] is the count
        }, {
            name: 'Female',
            data: femaleCounts.map(entry => entry[1])  // entry[1] is the count
        }],
        chart: {
            type: 'bar',
            height: 350,
            toolbar: {
                show: false,
            },
        },
        grid: {
            borderColor: '#e9ecef',
        },
        plotOptions: {
            bar: {
                horizontal: false,
                columnWidth: '40%',
                endingShape: 'rounded'
            },
        },
        dataLabels: {
            enabled: false
        },
        stroke: {
            show: true,
            width: 2,
            colors: ['transparent']
        },
        colors: ['#396cf0', '#53c797', '#f1b561'],
        xaxis: {
            categories: maleCounts.map(entry => entry[0])  // entry[0] is the date
        },
        yaxis: {
            title: {
                text: 'Patients',
    
                style: {
                    colors: ['#8492a6'],
                    fontSize: '13px',
                    fontFamily: 'Inter, sans-serif',
                    fontWeight: 500,
                },
            },
        },
        fill: {
            opacity: 1,
        },
        tooltip: {
            y: {
                formatter: function (val) {
                    return val + " Patients"
                }
            }
        }
    };
    
    var chart1 = new ApexCharts(document.querySelector("#dashboard"), options1);
    chart1.render();
} catch (error) {
    
}

try {
    var options2 = {
        chart: {
            height: 350,
            type: 'radialBar',
            dropShadow: {
              enabled: true,
              top: 10,
              left: 0,
              bottom: 0,
              right: 0,
              blur: 2,
              color: '#45404a2e',
              opacity: 0.35
            },
        },
        colors: ['#396cf0', '#53c797', '#f1b561', '#f0735a'],
        plotOptions: {
            radialBar: {
                track: {
                  background: '#b9c1d4',
                  opacity: 0.5,            
                },
                dataLabels: {
                    name: {
                        fontSize: '22px',
                    },
                    value: {
                        fontSize: '16px',
                        color: '#8997bd',
                    },
                    total: {
                        show: true,
                        label: 'Total',
                        color: '#8997bd',
                        formatter: function (w) {
                            // By default this function returns the sum of all series. 
                            return patientCounts.reduce((a, b) => a + b, 0)
                        }
                    }
                }
            }
        },
        series: patientCounts,
        labels: departmentNames,
    }

    var chart2 = new ApexCharts(document.querySelector("#department"),options2);
    chart2.render();
} catch (error) {
    
}