
function results_page_groupe_detail() {
    
    //back button
    $('#etape3_back_button_detail').on('click',function() {
        let id=$(this).data('goid');
        window.document.location.href='/results_detail.html?id='+id; 
    });
    
    
}