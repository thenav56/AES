// AJAX for posting
function evaluate_essay() {
    $.ajax({
        url : "", // the endpoint
        type : "POST", // http method
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        data : { essay_text : $('#essay-text').val() }, // data sent with the post request

        // handle a successful response
        success : function(json) {
            show_form_response = `
                <div class='text-center alert ${json.alert}'>
                    <a href='#' class='close' data-dismiss='alert' aria-label='close'>&times;</a>
                    <strong>${json.scored_message}</strong>
                    You Have Scored Marks of : ${json.marks_scored}
                </div>`;
            //$('#essay-text').val(''); // remove the value from the input
            $("#show-form-response").append(show_form_response);
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });

};

// Submit post on submit
$('#essay-evaluate-form').on('submit', function(event){
    event.preventDefault();
    evaluate_essay();
});
