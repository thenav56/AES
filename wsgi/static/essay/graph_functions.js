function render_histogram(div_id, resp_data){
    var trace1 = {
      x: resp_data.original_x,
      y: resp_data.predicted_y,
      name: 'Predicted',
      marker: {color: 'rgb(55, 83, 109)'}, 
      type: 'bar'
    };

    var trace2 = {
      x: resp_data.original_x,
      y: resp_data.original_y,
      name: 'Original',
      marker: {color: 'rgb(26, 118, 255)'}, 
      type: 'bar'
    };

    var data = [trace1, trace2];

    var layout = {
      title: 'Original Vs Predicted Histogram',
      xaxis: {
          title: 'Score Classes',
          tickfont: {
          size: 14, 
          color: 'rgb(107, 107, 107)'
        }}, 
      yaxis: {
        title: 'Score',
        titlefont: {
          size: 16, 
          color: 'rgb(107, 107, 107)'
        }, 
        tickfont: {
          size: 14, 
          color: "rgb(107, 107, 107)"
        }
      }, 
      legend: {
        x: 0, 
        y: 1.0, 
        bgcolor: 'rgba(255, 255, 255, 0)',
        bordercolor: 'rgba(255, 255, 255, 0)'
      }, 
      barmode: 'group',
      bargap: 0.15,
      bargroupgap: 0.1
    };

    Plotly.newPlot(div_id, data, layout);
};

function render_roc(div_id, resp_data){
    var trace1 = {
      x: [0, 1],
      y: [0, 1],
      name: 'Good',
      type: 'scatter'
    };
    resp_data.original_x.push(1)
    resp_data.original_y.push(1)
    var trace2 = {
      x: resp_data.original_x,
      y: resp_data.original_y,
      name: 'ROC Curve',
      type: 'scatter'
    };
    var data = [trace1, trace2];
    var layout = {
      title: 'ROC Curve',
      xaxis: {
        title: 'False Positive Rate(1 - Specificity)',
        titlefont: {
          size: 16,
          color: '#7f7f7f'
        }
      },
      yaxis: {
        title: 'True Positive Rate(Sensitivity)',
        titlefont: {
          size: 16,
          color: '#7f7f7f'
        }
      }
    };
    Plotly.newPlot(div_id, data, layout);
};


function render_scatter(div_id, resp_data){

    var data = [];
    var index = 1;

    for(i=0; i<resp_data.class_data.length; i++){
        index += 1 ;
        var trace = {
              x: resp_data.class_data[i].x_data,
              y: resp_data.class_data[i].y_data,
              mode: 'markers',
              type: 'scatter',
              name: 'Score '+index,
              marker: { size: 12 }
            };
        data.push(trace)
    };

    console.log(data)
    //var trace2 = {
      //x: [1.5, 2.5, 3.5, 4.5, 5.5],
      //y: [4, 1, 7, 1, 4],
      //mode: 'markers',
      //type: 'scatter',
      //name: 'Team B',
      //text: ['B-a', 'B-b', 'B-c', 'B-d', 'B-e'],
      //marker: { size: 12 }
    //};


    var layout = {
      xaxis: {
        range: [ 0, 20 ]
      },
      yaxis: {
        range: [0, 20]
      },
      title:'Data Scatter Diagram'
    };

    Plotly.newPlot(div_id, data, layout);
};



//temporary for case study
function render_histogram_casestudy(div_id, resp_data){
    var trace1 = {
      x: resp_data.predicted_x,
      y: resp_data.predicted_y,
      name: 'Predicted',
      marker: {color: 'rgb(55, 83, 109)'}, 
      type: 'bar'
    };

    var trace2 = {
      x: resp_data.original_x,
      y: resp_data.original_y,
      name: 'Original',
      marker: {color: 'rgb(26, 118, 255)'}, 
      type: 'bar'
    };

    var data = [trace1, trace2];

    var layout = {
      title: 'Pinnacle School Case Study',
      xaxis: {
          title: 'Students',
          tickfont: {
          size: 14, 
          color: 'rgb(107, 107, 107)'
        }}, 
      yaxis: {
        title: 'Score',
        titlefont: {
          size: 16, 
          color: 'rgb(107, 107, 107)'
        }, 
        tickfont: {
          size: 14, 
          color: "rgb(107, 107, 107)"
        }
      }, 
      legend: {
        x: 0, 
        y: 1.0, 
        bgcolor: 'rgba(255, 255, 255, 0)',
        bordercolor: 'rgba(255, 255, 255, 0)'
      }, 
      barmode: 'group',
      bargap: 0.15,
      bargroupgap: 0.1
    };

    Plotly.newPlot(div_id, data, layout);
};

function render_confusion(div_id, json){

    var data = [
      {
        x: json.x,
        y: json.y,
        z: json.matrix,
        colorscale: "Jet", 
        name: "trace0", 
        type: "heatmap"
      }
    ];

    var layout = {
      barmode: "overlay", 
      title: "Confusion Matrix", 
      xaxis: {
        title: "Predicted value", 
        titlefont: {
          size: 18
        }
      }, 
      yaxis: {
        title: "True Value", 
        titlefont: {
          size: 18
        }
      }
    };

    Plotly.plot(div_id, data, layout);
};
