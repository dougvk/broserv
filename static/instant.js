var runningRequest = false;
var request;
//Identify the typing action
$(document).ready(function() {
    $('input#query').keyup(function(event) {
        event.preventDefault();

        var $query = $(this);

        if ($query.val() === '') {
            $('div#results').html('');
            return false;
        }

        //Abort opened requests to speed it up
        if (runningRequest) {
            request.abort();
        }

        runningRequest = true;
        request = $.ajax({
            url: 'http://api.thriftdb.com/test_bucket/files/_search',
            dataType: 'jsonp',
            data: {
                q: $query.val()
            },
            success: function(data) {
                // word
                var items = [];

                $.each(data.results, function(index, val) {
                    items.push('<li id="' + index + '">' + val.item.name + '</li>');
                    items.push('<li id="' + index + '">' + val.item.path + '</li>');
                });

                $('div#results').html(items.join(''));
            }
        });

        $('form').submit(function(event) {
            event.preventDefault();
        });
    });
});
