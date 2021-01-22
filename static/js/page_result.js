
function results_page() {

    $('.solution_buton').on('click',function() {
        window.document.location.href='/results_detail.html?id='+this.dataset.goid;
    });
    
    $('#reset_results').on('click',function() { 
        reset_results();
    });
    
    if($('#simulation_status').val()==0) {
        $('#modal_wait').show();
        //progress_status = window.setInterval(check_progress,2000);
        //setTimeout(check_progress, 300);
        $.post( "/results_ajax?action=wait_results")
        .done(function( rep ) {
            console.log('Simulation finished');
            check_progress();
        })
        .fail(function() {
            console.log( "Simulation error" );
        });
    }
    
    if($('#simulation_status').val()==1) {
        $('#modal_wait').show();
        progress_status = window.setInterval(check_progress,2000);
        setTimeout(check_progress, 300);
    }
}

/*function save_results(reseau) {
    $.post("/results_ajax?action=save_results", {data : JSON.stringify(reseau)})
    .done(function(rep) {
        console.log(rep);
        window.document.location.href='/results.html';
    })
}*/


function reset_results() {
    $.get( "/results_ajax?action=reset_results")
    .done(function( rep ) {
        window.location.href="/";
    })
    .fail(function() {
        alert( "Connexion error" );
    });
}


function check_progress() {
    console.log( "progress check" );
    $.post( "/results_ajax?action=progress_results")
    .done(function( rep ) {
        console.log( "progress update" + rep);
        rep=rep.split('@');
        //$('#simulation_progress').val(rep[0]);
        $('#simulation_progress_txt').html(rep[0]);
        
        if(parseInt(rep[1]) != 1 ) {
            clearInterval(progress_status);
            setTimeout(function() {
                window.document.location.href='/results.html';
            }, 2000);
        }
        
    })
    .fail(function() {
        clearInterval(progress_status);
        console.log( "progress fail" );
    });
    
}