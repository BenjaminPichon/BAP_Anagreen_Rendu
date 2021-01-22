
function index_page_detail() {
    
    json_data=JSON.parse($('#json_data_index_detail').val());

    // load the "select flux" select menu that let chose an active flux
    let data_flux=json_data.data_flux;
    let select='Select flux: <select id="menu_select_detailflux">';
    select+='<optgroup label="Hot flux">';
    for(let i in data_flux['hotcold']) {
        if(data_flux['hotcold'][i]=="hot" && data_flux['active'][i]=="yes") {
            select+='<option value="'+data_flux['id'][i]+'">';
            select+=data_flux['name'][i];
            select+='</option>';
        }
    }
    select+='</optgroup>';
    select+='<optgroup label="Cold flux">';
    for(let i in data_flux['hotcold']) {
        if(data_flux['hotcold'][i]=="cold" && data_flux['active'][i]=="yes") {
            select+='<option value="'+data_flux['id'][i]+'">';
            select+=data_flux['name'][i];
            select+='</option>';
        }
    }
    select+='</optgroup>';
    select+='</select>';
    console.log(select);
    $('#flux_selector').html(select);
    
    var url = new URL(window.document.location.href);
    var id = url.searchParams.get("id");
    console.log(id);
    $('#flux_selector select').val(id);
    
    //detect if we want to display one other flux
    $('#flux_selector select').on('change',function() {
        let newid= $('#flux_selector select').val();
        window.document.location.href='/index_detail.html?id='+newid;
    });
    
    $('#etape1_back_button').on('click',function() {
        window.document.location.href='/';
    });
}