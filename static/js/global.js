// global vars, should be accessible from everywhere
let json_data={};
let timer_floodchanges=false;
let progress_status=false;



//  indicate that a change in the map information should not trigger a DB change
// - if we "move" a flux, bokeh detect the change and trigger an ajax request, so we sve in DB => leave noupdate_select=false;
// - if we trigger a modification like changing the color of a flux and doesn't want to triger DB update, we set noupdate_select=true;
// - if we want to manually remove a flux or change details (like name), we do it manually, make ajax reuest and ask bokeh to do nothing with noupdate_select=true;
// - so we can manually control the process (like making some controls before doing an ajax request)
let noupdate_select=false;

// The page_index function is called into the index.html templetes.

//initialization: load json_data

$(document).ready(function() {
    if($('#json_data_index').length) {
        if ($('#json_data_index').val() != "") {
            setup_page();
        }
        if ($('#dropfile').length) {
            setup_upload();
        } 
    }
    if($('#json_data_index_detail').length) {
        index_page_detail();
    }
    if($('#json_data_params').length) {
        params_page();
    }
    if($('#json_data_result').length) {
        results_page();
    }
    if($('#json_data_result_detail').length) {
        results_page_detail();
    }
    if($('#json_data_result_group_detail').length) {
        results_page_groupe_detail();
    }
    if($('#json_data_history').length) {
        history_page();
    }
    
    $(document).keyup(function(e) {
        if (e.keyCode == 27) { // escape key maps to keycode `27`
            close_popups() 
        }
    });
    
    $('#reset_button').on('click',function() { 
        reset();
    });
    
    $('.modal_close_button').on('click',function() { 
        close_popups();
    });
});


function close_popups() {
    $('#modal_edit_flux').hide();
    $('#modal_edit_flux_detaildata').hide();
    $('#modal_rename_zone').hide();
    $('#modal_history_preview').hide();
}


//reset button clicked, make ajax call to reload database from model and reload page
function reset() {
    if(confirm('Warning, il will clear all history and current calculation.')) {
        $.get( "/ajax_setup?action=reset")
        .done(function( rep ) {
			console.log(rep);
			
            window.location.href="/";
        })
        .fail(function() {
            alert( "Connexion error" );
        });
    }
}

function is_empty(form) {
    var empty = false;
    $('input[type="text"]').each(function(){
        if($(this).val()==""){
            empty = true;
        }
    });
    return empty;
}


