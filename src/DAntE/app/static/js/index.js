$('#inputGroupFile').on('change', function(){
    var fileName = $(this).val().replace('C:\\fakepath\\', '');
    $(this).next('.custom-file-label').html(fileName);
});