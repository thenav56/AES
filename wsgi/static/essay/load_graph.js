// AJAX for posting
function load_graph(div_id, graph_name) {
    $.ajax({
        url : "graph_data", // the endpoint
        type : "POST", // http method
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        data : {graph_name: graph_name}, // data sent with the post request

        // handle a successful response
        success : function(json) {
            $('#'+div_id).css({'width': '960px', 'height': '400px'})
            if(graph_name == 'HISTOGRAM'){
                render_histogram(div_id, json)
            }else if(graph_name == 'ROC'){
                render_roc(div_id, json)
            }else if(graph_name == 'SCATTER'){
                render_scatter(div_id, json)
            }else if(graph_name == 'HISTOGRAM-casestudy'){
                if(json.error != undefined){
                    $('#'+div_id).css({'width': '0px', 'height': '0px'})
                }else{
                    render_histogram_casestudy(div_id, json)
                }
            }else if(graph_name == 'CONFUSION'){
                render_confusion(div_id, json)
            };
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            $('#'+div_id).html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                           " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });

};

// Submit post on submit
$(document).ready(function() {
    load_graph("graph_1", 'HISTOGRAM');
    load_graph("graph_2", 'ROC');
    load_graph("graph_3", 'SCATTER');
    load_graph("graph_4", 'HISTOGRAM-casestudy');
    load_graph("graph_5", 'CONFUSION');
});
