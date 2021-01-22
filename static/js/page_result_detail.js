
function results_page_detail() {

    json_data=JSON.parse($('#json_data_result_detail').val());
    
    // load tables on left
    load_tables_result_detail();
    
    $('#button_deselect_all').on('click',deselect_all_groupes_results);
    
    
    // solution selector
    let solution=json_data.solution;
    let select='Select flux: <select id="menu_select_detailflux">';
    for(let i in solution['id']) {
        select+='<option value="'+solution['id'][i]+'">';
        select+='Solution rank: '+solution['rank'][i];
        select+='</option>';
    }
    select+='</select>';
    $('#flux_selector').html(select);
    
    var url = new URL(window.document.location.href);
    var id = url.searchParams.get("id");
    $('#flux_selector select').val(id);
    
    $('#flux_selector select').on('change',function() {
        let newid= $('#flux_selector select').val();
        window.document.location.href='/results_detail.html?id='+newid;
    });
    
    
}

function deselect_all_groupes_results() {
    $('#table_couples tbody input').prop('checked',false);
    
    let list_groups=json_data.list_groups;
    
    for(let g in list_groups) {
        ds_flux_couples=Bokeh.documents[0].get_model_by_name('name_couples_lines_'+list_groups[g]);
        for(let i in ds_flux_couples.data['colors']) {
            ds_flux_couples.data['colors'][i]='rgba(0, 204, 0, 0.5)';
        }
        ds_flux_couples.change.emit();
    }
    
    ds_flux=Bokeh.documents[0].get_model_by_name('name_souce_flux');
    //on reset la couleur des flux
    for(let i in ds_flux.data['color']) {
        if(ds_flux.data['hotcold'][i]=='hot') {
            ds_flux.data['color'][i]='rgba(255, 0, 0, 0.5)';
        }
        if(ds_flux.data['hotcold'][i]=='cold') {
            ds_flux.data['color'][i]='rgba(0, 0, 255, 0.5)';
        }
    }
    ds_flux.change.emit();
}



// load hot/cold/zones tables on the left
function load_tables_result_detail() {
    
    let table_body_couples='';

    for(let i in json_data['list_groups']) {
        table_body_couples+='<tr><td><input type="checkbox" id="'+json_data['list_groups'][i]+'"></td><td><label for="'+json_data['list_groups'][i]+'"> ';
        table_body_couples+=json_data['list_groups'][i]+'';
        table_body_couples+='</label></td></tr>';
    }
  
    $('#etape3_back_button').on('click',function() { window.document.location.href='/results.html'; });
    
    $('#table_couples tbody').html(table_body_couples);
    
    //detect if we clicked on a checkbox flux
    $('#table_couples tbody input').on('change',function() {
        let detail_groupe=json_data.groupe;
    
        let id=this.id;
        
        ds_flux_couples=Bokeh.documents[0].get_model_by_name('name_couples_lines_'+id);
        // Color in RGBA form (reg green blue alpha), alpha is used to manage opacity/transparency
        //we reset couple colors (green line) with default color (0.5 alpha)
        for(let i in ds_flux_couples.data['colors']) {
            ds_flux_couples.data['colors'][i]='rgba(0, 204, 0, 0.5)';
        }

        //for each couple, we set selected color (1.0 alpha)
        $('#table_couples tbody input').each(function() {
           let currid=this.id;
           currds_flux_couples=Bokeh.documents[0].get_model_by_name('name_couples_lines_'+id);
           if(this.checked) {
                for(let i in currds_flux_couples.data['colors']) {
                    currds_flux_couples.data['colors'][i]='rgba(0, 204, 0, 1)';
                }
            }
            currds_flux_couples.change.emit();
        })
        ds_flux=Bokeh.documents[0].get_model_by_name('name_souce_flux');
        
        //we do the same for the flux, we reset their colors
        for(let i in ds_flux.data['color']) {
            if(ds_flux.data['hotcold'][i]=='hot') {
                ds_flux.data['color'][i]='rgba(255, 0, 0, 0.5)';
            }
            if(ds_flux.data['hotcold'][i]=='cold') {
                ds_flux.data['color'][i]='rgba(0, 0, 255, 0.5)';
            }
        }
        
        //and for each one
        $('#table_couples tbody input').each(function() {
            let currid=this.id;
            if(this.checked) {
                // (that si checked)
                let listselect=[]
                for(let i in detail_groupe[currid]) {
                    listselect.push(detail_groupe[currid][i]['flux_id']);
                }
                //we set selected color  (1.0 alpha)
                for(let i in ds_flux.data['color']) {
                    if(listselect.indexOf(parseInt(ds_flux.data['id'][i])) != -1) {
                        if(ds_flux.data['hotcold'][i]=='hot') {
                            ds_flux.data['color'][i]='rgba(255, 0, 0, 1)';
                        }
                        if(ds_flux.data['hotcold'][i]=='cold') {
                            ds_flux.data['color'][i]='rgba(0, 0, 255, 1)';
                        }
                    }
                }
            }   
        })    
        ds_flux.change.emit();
        
        load_result_details();
    });
}


// if exactly one checkbox is selected, display couple details
function load_result_details() {
    let list_groups=json_data.list_groups;
    let detail_groupe=json_data.groupe;
    let distance_all_lines=json_data.distance_all_lines;
	let exchangers_names = json_data.exchangers_names;
    let numgroupes=0;
    let selectedgroup=-1;
    
    for(let i in list_groups) {
        if($('#'+list_groups[i]).prop('checked')) {
            numgroupes++;
            selectedgroup=list_groups[i];
        }
    }
    
    //exactly one is checked, we display details
    if(numgroupes==1) {
        $('#help_area').hide();
        $('#detail_area').show();
        
        let detail_hot='';
        let detail_cold='';
        let detail_exchanger='';
        
        //list of flux of the couple
        for(let i in detail_groupe[selectedgroup]) {
            let info=detail_groupe[selectedgroup][i]
            if(info['hotcold']=='hot') {
                detail_hot+='<tr><td>'+info['flux_name']+'<br>('+info['flux_media']+' - class '+info['flux_fclass']+')</td></tr>';
            }
            if(info['hotcold']=='cold') {
                detail_cold+='<tr><td>'+info['flux_name']+'<br>('+info['flux_media']+' - class '+info['flux_fclass']+')</td></tr>';
            }
        }
		console.log(detail_groupe);
        //linear meters of the exchanger
        detail_exchanger+='<tr><td>Name: '+exchangers_names[selectedgroup]+'</td></tr>';
        detail_exchanger+='<tr><td>Linear meters: '+distance_all_lines[selectedgroup]+'</td></tr>';
		detail_exchanger+='<tr><td>Phi: '+detail_groupe[selectedgroup][0]["Phi"]+'</td></tr>';
		detail_exchanger+='<tr><td>h_global: '+detail_groupe[selectedgroup][0]["h_global"]+'</td></tr>';
		detail_exchanger+='<tr><td>S1: '+ detail_groupe[selectedgroup][0]["S1"]+' m²</td></tr>';
        detail_exchanger+='<tr><td>S2: '+detail_groupe[selectedgroup][0]["S2"] +' m²</td></tr>';
		detail_exchanger+='<tr><td>Price: '+detail_groupe[selectedgroup][0]["Price"]+'</td></tr>';
        let resultid = $('#flux_selector select').val();
        detail_exchanger+='<tr><td  style="text-align:center;"><input type="button" id="go_detail_button2" value="Details" data-goid="'+selectedgroup+'" data-resultid="'+resultid+'"></td></tr>';
    
        $('#table_details_hot tbody').html(detail_hot);
        $('#table_details_cold tbody').html(detail_cold);
        $('#table_details_exchanger tbody').html(detail_exchanger);
        
        $('#go_detail_button2').on('click',function() { window.document.location.href='/results_group_detail.html?id='+this.dataset.goid+'&resultid='+this.dataset.resultid; });
        
    } else {
        $('#help_area').show();
        $('#detail_area').hide();
    }
    
    
    
    
    
}