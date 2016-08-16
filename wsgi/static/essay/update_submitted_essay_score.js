// AJAX for posting
function update_essay_original_score(formDetails) {
    $.ajax({
        url : "/essay/update_submitted_essay_score", // the endpoint
        type : "POST", // http method
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        data : formDetails.serialize(), // data sent with the post request

        // handle a successful response
        success : function(json) {
            var show_form_response = `
                    <div class='text-center alert alert-${json.alert} alert-update-submitted-essay'>
                        <a href='#' class='close' data-dismiss='alert' aria-label='close'>&times;</a>
                            ${json.response}
                    </div>`;
            formDetails.children("#show-update-essay-response").html(show_form_response);
            createAutoClosingAlert(".alert-update-submitted-essay", 1000);
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
$(document).ready(function() {
    $('.essaysubmitted-form').on('submit', function(event){
        event.preventDefault();
        var  formID = $(this).attr('id');
        var formDetails = $(this);
        update_essay_original_score(formDetails);
    });
});
