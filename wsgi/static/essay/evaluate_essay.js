// AJAX for posting
function evaluate_essay() {
    $.ajax({
        url : "/essay/evalute_essay_text", // the endpoint
        type : "POST", // http method
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        data : $('#essay-evaluate-form').serialize(), // data sent with the post request

        // handle a successful response
        success : function(json) {
            var show_form_response = ''
            if (json.error != undefined){
                show_form_response = `
<div class="modal fade " id="result-lg" tabindex="-1" role="dialog">
  <div class="modal-dialog modal-lg" role="document">

        <div class='text-center alert alert-danger'>
            <div class="content">
                <strong><font size="12px">${json.error_code} Error</font></strong>
                <p><font size="3px">${json.error}</font></p>
            </div>
        </div>

    </div>
</div>
                    `;
            }else{
                show_form_response = `
<div class="modal fade " id="result-lg" tabindex="-1" role="dialog">
  <div class="modal-dialog modal-lg" role="document">

        <div class='text-center alert ${json.alert}'>
            <div class="content">
                <strong><font size="12px">${json.scored_message}</font></strong>
            </div>
        </div>

    <div class="modal-content">
        <div class="modal-body">
            <h4>Summary</h4>
        </div>
        <div class="modal-body">
            <div class="row">
                <div class="col-lg-6">
                    Grammer
                </div>
                <div class="col-lg-6">
                    <div class="progress" style="">
                      <div class="progress-bar progress-bar-primary progress-bar-striped active" role="progressbar" aria-valuenow="60"
                      aria-valuemin="0" aria-valuemax="100" style="width: ${json.grammer}%;">
                        <span class="sr-only">60%</span>
                      </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-lg-6">
                    Spell Correction
                </div>
                <div class="col-lg-6">
                    <div class="progress" style="">
                      <div class="progress-bar progress-bar-primary progress-bar-striped active" role="progressbar" aria-valuenow="60"
                      aria-valuemin="0" aria-valuemax="100" style="width: ${json.cspell}%;">
                        <span class="sr-only">60%</span>
                      </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-lg-6">
                    Bag Of Words
                </div>
                <div class="col-lg-6">
                    <div class="progress" style="">
                      <div class="progress-bar progress-bar-primary progress-bar-striped active" role="progressbar" aria-valuenow="60"
                      aria-valuemin="0" aria-valuemax="100" style="width: ${json.bagofwords}%;">
                        <span class="sr-only">60%</span>
                      </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="text-center">
                   <h1>${json.marks_scored}</h1><span class="glyphicon glyphicon-certificate"></span>
                   <h3>Final Score</h3>
                </div>
            </div>

        </div>
    </div>

  </div>
</div>
                    `;
                //$('#essay-text').val(''); // remove the value from the input
            }
            $("#show-form-response").html(show_form_response);
            $("#result-lg").modal('show');
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
    $('#essay-evaluate-form').on('submit', function(event){
        event.preventDefault();
        evaluate_essay();
    });
});
