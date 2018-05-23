/**
 * Created by vauser on 19/5/18.
 */
function render_response(response) {
    $("#content_list").html(response['result']).show();
}

function validate_inputs(identifier) {
    empty = [];
    $('input[name^="' + identifier+ '"]').each(function () {
        var i = $(this).val().trim();
        if (!i) {
            name = $(this).attr('name').replace(identifier, '');
            empty.push(name);
        }
    });

    return empty;
}