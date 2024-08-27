$(document).ready(function() {
    $('#mentor, #date').change(function() {
        var mentor = $('#mentor').val();
        var date = $('#date').val();
        if (mentor && date) {
            $.ajax({
                url: '/available_times',
                data: { mentor: mentor, date: date },
                success: function(response) {
                    $('#time').empty();
                    $('#time').append('<option value="">Select a time slot</option>');
                    $.each(response, function(index, time) {
                        $('#time').append('<option value="' + time + '">' + time + '</option>');
                    });
                }
            });
        }
    });
});
