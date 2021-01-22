
function params_page() {
    
    // add min/max range and value on input type=range 
    $('input[type="range"]').each(function() {
        $(this).parent().find('p').append(' <span id="inputrange_labelval_'+this.id+'">'+this.value+'</span>')
        $(this).before('<span>'+this.min+'</span> ' );
        $(this).after(' <span>'+this.max+'</span>' );
    });
    
    // update values on input type=range 
    $('input[type="range"]').on('change', function() {
        $('#inputrange_labelval_'+this.id).html(this.value);
    });
}
