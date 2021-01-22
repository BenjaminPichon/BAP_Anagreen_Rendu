
function history_page() {
   
    $('.history_preview_button').on('click',function() { 
        id=$(this).data('goid');
        $.get( "/history_ajax?action=history_preview&id="+parseInt(id))
        .done(function( rep ) {
            let data = JSON.parse(rep)
            console.log(data)
            out='';
            maxprev=5; // Limit preview to 5 first results
            for(let i in data['solution']) {
                maxprev--;
                if(maxprev>=0) {
                    out+='<tr>';
                    out+='<td>'+data['solution'][i]['rank']+'</td>';
                    out+='<td>'+data['solution'][i]['savedEnergy']+'</td>';
                    out+='<td>'+data['solution'][i]['capex']+'</td>';
                    out+='<td>'+data['solution'][i]['roi']+'</td>';
                    out+='<td>'+data['solution'][i]['CO2Savings']+'</td>';
                    out+='<td>'+data['solution'][i]['score']+'</td>';
                    out+='</tr>';
                }
            }
            $('#history_preview_table tbody').html(out);
            $('#modal_history_preview').show();
        })
        .fail(function() {
            alert( "Connexion error" );
        });
    });
    
    
    $('.history_load_button').on('click',function() { 
        let params_changed = parseInt($('#params_changed').val());
        if(params_changed) {
            // if(!confirm('Parameters have been changed and not stored in history. Are you sure you want to load?')) {
                // return;
            // }
        }
        
        $('#modal_wait_load').show();
        id=$(this).data('goid');
        $.get( "/history_ajax?action=history_restore&id="+parseInt(id))
        .done(function( rep ) {
            console.log(rep)
            $('#modal_wait_load').hide();
        })
        .fail(function() {
            alert( "Connexion error" );
        });
    });
    
    
    
}
