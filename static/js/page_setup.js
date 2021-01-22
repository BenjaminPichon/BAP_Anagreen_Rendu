//look at global.js for the menaing of the variable "noupdate_select"

function setup_page() {

    //Set active the list of flux and the next button. The list and button are disabled by default as when the map isn't uploaded yet
    $('#list_of_flux input').prop("disabled", false ); 
    $('#list_of_flux select').prop("disabled", false ); 
    $('#etape1_next_step_button').prop("disabled", false ); 

    json_data=JSON.parse($('#json_data_index').val());
    
    // add "selected" attribute to know if flux is selected or not
    json_data.data_flux['selected']=new Array(json_data.data_flux['name'].length).fill(false);
    json_data.data_notouch_zones['selected']=new Array(json_data.data_notouch_zones['name'].length).fill(false);
    
    // load tables on left and the dropdown with checkbox
    console.log ("Chargement du document")
    load_tables();
    multiselect_to_dropdown('fclass_filter');
    
    //Listener when the filter is trigged
    $('#fclass_filter').on('change',load_tables);
   
    //manage events (on click) for events not dynamically generated
    $('#etape1_next_step_button').on('click',function() {
        window.document.location.href='/parametrization.html';
    });
    $('#button_deselect_all').on('click',function() {
        deselect_all();
    });
    $('#modal_flux_submit').on('click',function() {
        modal_flux_submit();
    });
    $('#modal_flux_cancel').on('click',function() {
        close_popups();
    });
    $('#modal_fluxdata_cancel').on('click',function() {
        close_popups();
    });
    $('#button_empty_trash').on('click',function() {
        button_empty_trash();
    });
    $('#button_restore_selected').on('click',function() {
        button_restore_selected();
    });
    $('#modal_fluxdata_submit').on('click',function() {
        modal_fluxdata_submit();
    });
    $('#modal_flux_editdetaildata').on('click',function() {
        modal_flux_editdetaildata();
    });
    $('#modal_zone_submit').on('click',function() {
        modal_zone_submit();
    });
    $('#modal_flux_remove').on('click',function() {
        let modal_id=$('#modal_flux_id').val();
        remove_flux(modal_id);
        close_popups();
    });
    $('#modal_zone_remove').on('click',function() {
        let modal_id=$('#modal_zone_id').val();
        remove_zone(modal_id);
        close_popups();
    });
    $('span#fclass_filter_sk_span').change(function() {
        var filter = $(this).val();
        filterList(filter);
    });
}

function setup_upload() {
    $("#fclass_filter").hide();
    $('#list_of_flux').css("pointer-events", "none")// Undo the clic on the list. Need to upload the map to set the flux
    
    $(document).on('dragenter', '#dropfile', function() {
        $(this).css('border', '3px dashed red');
        return false;
    });

    $(document).on('dragover', '#dropfile', function(e){
            e.preventDefault();
            e.stopPropagation();
            $(this).css('border', '3px dashed red');
            return false;
    });

    $(document).on('dragleave', '#dropfile', function(e) {
            e.preventDefault();
            e.stopPropagation();
            $(this).css('border', '3px dashed #BBBBBB');
            return false;
    });

    $(document).on('drop', '#dropfile', function(e) {
        if(e.originalEvent.dataTransfer) {
            if(e.originalEvent.dataTransfer.files.length) {
                // Stop the propagation of the event
                e.preventDefault();
                e.stopPropagation();
                $(this).css('border', '3px dashed green');
                // Main function to upload
                upload(e.originalEvent.dataTransfer.files);
            }  
        }
        else {
            $(this).css('border', '3px dashed #BBBBBB');
        }
    });

    // A revoir 
	document.getElementById('file_picker').addEventListener("change", function(e) {
        e.preventDefault();
        upload(e.target.files);	
    }); 

    /*$("input#file_picker").on('change', function () {
    $('form#form_upload_map').submit();
    });*/
}

function upload(files) {

    // Only process image files.
    if (!files[0].type.match('image/*')) {
        alert("Vous ne pouvez qu'uploder des images en tant que plan de mass");
        return false ;
    }

    //Format the file for upload
    var formData = new FormData();
    formData.append("file2upload", files[0]);

    var req = {
        url: "/upload",
        type: "post",
        processData: false,
        contentType: false,
        data: formData,
    };

    $.ajax(req).done(function() {
        window.location.reload();
    }); 
}

function modal_flux_submit() {
    noupdate_select=true;
    let modal_id=$('#modal_flux_id').val();
    json_data.data_flux['name'][modal_id]=$('#modal_flux_name').val();
    json_data.data_flux['hotcold'][modal_id]=$('#modal_flux_hotcold').val();
    json_data.data_flux['media'][modal_id]=$('#modal_flux_media').val();
    json_data.data_flux['fclass'][modal_id]=$('#modal_flux_fclass').val();
    noupdate_select=false;
    load_graph_flux();
    update_flux(json_data.data_flux);
    close_popups();
}

function modal_zone_submit() {
    noupdate_select=true;
    let modal_id=$('#modal_zone_id').val();
    let modal_name=$('#modal_zone_name').val();
    json_data.data_notouch_zones['name'][modal_id]=modal_name;
    load_graph_zones();
    noupdate_select=false;
    update_zones(json_data.data_notouch_zones);
    close_popups();
}

function modal_flux_editdetaildata() {
    let idflux2=$('#modal_flux_id').val();
    close_popups();
    $('#modal_edit_flux_detaildata').show();
    id_db_flux=json_data.data_flux['id'][idflux2]
    $('#modal_flux_id_detaildata').val(id_db_flux);
    $.get( "/ajax_setup?action=get_flux_details&id="+id_db_flux)
    .done(function( rep ) {
        // we load the flux detail in a tbbuled and newline version for textarea
        rep=JSON.parse(rep);
        
        // manually list elements to lod to be certain to get the good order
        list=["id","tempIn","tempOut","Cp","flow","timestamp"]
        
        out=list.join("\t")+"\n"; //headers
        let linenum=1;
        for (linenum in rep) {
            let line=[]
            for (i in list) {
                line.push(rep[linenum][list[i]]);
            }
            out+=line.join("\t")+"\n";
        }
        $('#textare_flux_detaildata').val(out);
    })
    .fail(function() {
        alert( "Connexion error" );
    });
}


function modal_fluxdata_submit() {
    iddata=$('#modal_flux_id_detaildata').val();
    detaildata=$('#textare_flux_detaildata').val();
    
    $.post( "/ajax_setup?action=update_fluxdata", { iddata: iddata, detaildata: detaildata })
    .done(function( rep ) {
        close_popups();
    })
    .fail(function() {
        alert( "Connexion error" );
    });
}

// Function to search through the list of flux by name 
function search_flux_list() {
    //Declaration of all the variable for this function
    var input, word_filter, flux_list, i, txtvalue, flux_name, type_info, tag_info, media_info;
    input = document.getElementById("word_filter");
    word_filter = input.value.toUpperCase();
    flux_list = $('#table_flux > tbody > tr')
    for (i = 0; i < flux_list.length; i++) {
        //Gather informations relative to the flux
        flux_name = flux_list[i].getElementsByTagName("label")[0].innerText;
        type_info = flux_list[i].getElementsByTagName("text")[0].innerText.split(':')[1];
        tag_info = flux_list[i].getElementsByTagName("text")[1].innerText.split(':')[1];
        media_info = flux_list[i].getElementsByTagName("text")[2].innerText.split(':')[1];
        //Create the text variable containing all the informations
        txtvalue = flux_name + type_info + tag_info + media_info;
        //Hide all the elements of the list that don't match the input (word_filter) of the user
        if (txtvalue.toUpperCase().indexOf(word_filter) > -1) {
            flux_list[i].style.display = "";
        } 
        else {
            flux_list[i].style.display = "none";
        }
    }
}


// load hot/cold/zones tables on the left
function load_tables() {
    json_data=JSON.parse($('#json_data_index').val());
    let fclass_filter=$('#fclass_filter').val().map(Number);
    //let word_filter=$('#word_filter').val().toLowerCase();
    
    // hot/cold tables
    let data_flux=json_data.data_flux;
    let table_body_flux='';
    let table_body_trash='';
    
    for(let i in data_flux['hotcold']) {
        //filter by search (we search on the fields name/media and fclass) - > OLD VERSION 
        /*let item_list=[];
        let tmpitem='';
        let found=false;
        let search_list=word_filter.split(' ');
        item_list.push(data_flux['name'][i].toLowerCase());
        item_list.push(data_flux['media'][i].toLowerCase());
        if(data_flux['fclass'][i]==1) item_list.push('primary');
        if(data_flux['fclass'][i]==2) item_list.push('secondary');
        if(data_flux['fclass'][i]==3) item_list.push('tertiary');
        for(j in search_list) {
            for(k in item_list) {
                tmpitem=item_list[k].substring(0,search_list[j].length);
                if(search_list[j]==tmpitem) { found=true; }
            }
        } 
        if(!found) { continue; }
        */
        
        //filter by fclass
        if(fclass_filter.length && fclass_filter.indexOf(data_flux['fclass'][i])==-1) {
            continue;
        } 
        
        active = data_flux['active'][i] == 'yes'
        
        if(active) {
            table_body_flux+='<tr><td><div class="table_row_container"><div><input type="checkbox" id="flux_'+i+'"><label for="flux_'+i+'"><a href="/index_detail.html?id='+data_flux['id'][i]+'"> ';
            table_body_flux+=data_flux['name'][i]+'</label><i class="fas fa-info-circle"></i></a><i class="fas fa-trash-alt" onclick="disable_flux('+i+');" title="Put in trash"></i></div>';
            table_body_flux+='<div class="flux_details_container"><text class="list_flux_details">Type : '+data_flux['hotcold'][i]+' </text><text class="list_flux_details">Tag : '+data_flux['fclass'][i]+' </text><text class="list_flux_details">Media : '+data_flux['media'][i]+'</text></div>'
            table_body_flux+='</div></td></tr>';
        }
 
        // note: before, there was separate trash for hot and cold, no we all put in trash hot (labelled trash)
        if(!active) {
            table_body_trash+='<tr><td><input type="checkbox" id="flux_'+i+'"></td><td><label for="flux_'+i+'"> ';
            table_body_trash+=data_flux['name'][i]+' <i class="fas fa-trash-alt" onclick="remove_flux('+i+');" title="Delete"></i> <i class="fas fa-redo" title="Restore" onclick="restore_flux('+i+');"></i>';
            table_body_trash+='</label></td></tr>';
        }
        // Detect if we create a new flux, in case it opens the flux submission modal window 
        if(data_flux['name'][i].substr(data_flux['name'][i].length - 2)=="##") {
            data_flux['name'][i]=data_flux['name'][i].substr(0,data_flux['name'][i].length - 2)
            modal_edit_flux(i)
        }
    }
    
    $('#table_flux tbody').html(table_body_flux);
    $('#table_trash_flux tbody').html(table_body_trash);
    
    
    if(table_body_trash!='') {
        $('#trash_flux').show();

    } else {
        $('#trash_flux').hide();
    }

    //detect if we clicked on a checkbox flux
    $('#table_flux tbody input').on('change', function() {
            
        if(!json_data.data_flux['selected']) {
            json_data.data_flux['selected']=new Array(json_data.data_flux['name'].length).fill(false);
        }
        noupdate_select=true;
        let id=this.id.split('_')[1];
        json_data.data_flux['selected'][id]=this.checked;
        load_graph_flux();
        noupdate_select=false;
    });
    
    //detect if we rightclicked a flux
    $('#table_flux tbody tr').contextmenu(function(evt) {
        evt.preventDefault();
        let index=$(this).find('input').attr('id').split('_')[1];
        modal_edit_flux(index);
    });

    //zone table
    let data_notouch_zones=json_data.data_notouch_zones;
    let table_body_notouch_zones='';
    for(let i in data_notouch_zones['x']) {
        table_body_notouch_zones+='<tr><td><input type="checkbox" id="zone_'+i+'"></td><td><label for="zone_'+i+'"> ';
        table_body_notouch_zones+=data_notouch_zones['name'][i]+' <i class="fas fa-trash-alt" onclick="remove_zone('+i+');" title="Delete"></i>';
        table_body_notouch_zones+='</label></td></tr>';
    }
    $('#table_zones tbody').html(table_body_notouch_zones);
    
    //detect if we clicked on a checkbox zone
    $('#table_zones tbody input').on('change',function() {
            
        if(!json_data.data_notouch_zones['selected']) {
            json_data.data_notouch_zones['selected']=new Array(json_data.data_notouch_zones['name'].length).fill(false);
        }  
        noupdate_select=true;
        let id=$(this).attr('id').split('_')[1];
        json_data.data_notouch_zones['selected'][id]=this.checked;
        load_graph_zones();
        noupdate_select=false;
    });
    //detect if we rightclicked a zone
    $('#table_zones tbody tr').contextmenu(function(evt) {
        evt.preventDefault();
        $('#modal_rename_zone').show();
        let id=$(this).find('input').attr('id').split('_')[1];
        $('#modal_zone_id').val(id);
        $('#modal_zone_name').val(json_data.data_notouch_zones['name'][id]);
    });
}



// load/update graph to show selected hot/cold flux
function load_graph_flux() {
    ds_flux_start=Bokeh.documents[0].get_model_by_name('bokeh_souce_flux_start');
    ds_flux_end=Bokeh.documents[0].get_model_by_name('bokeh_souce_flux_end');
    
    let data_flux=json_data.data_flux;
    
    if(!data_flux['selected']) {
        data_flux['selected']=new Array(data_flux['name'].length).fill(false);
    }
    
    for(let i in data_flux['name']) {
        // calcul de la couleur du flux
        // Color in RGBA form (reg green blue alpha), alpha is used to manage opacity/transparency
        if(data_flux['hotcold'][i]=='hot') {
            if(data_flux['selected'][i]) {
                json_data.data_flux['color'][i]="rgba(255, 0, 0, 1)";
            } else {
                json_data.data_flux['color'][i]="rgba(255, 0, 0, 0.5)";
            }
        }
        if(data_flux['hotcold'][i]=='cold') {
            if(data_flux['selected'][i]) {
                json_data.data_flux['color'][i]="rgba(0, 0, 255, 1)";
            } else {
                json_data.data_flux['color'][i]="rgba(0, 0, 255, 0.5)";
            }
        }
    }
    ds_flux_start.data = json_data.data_flux;
    ds_flux_end.data = json_data.data_flux;

    ds_flux_start.change.emit();
    ds_flux_end.change.emit();
}

// load/update graph to show selected hot/cold zones
function load_graph_zones() {
    ds_notouch=Bokeh.documents[0].get_model_by_name('name_souce_notouchezone');
    
    let data_notouch_zones=json_data.data_notouch_zones;
    
    if(!data_notouch_zones['selected']) {
        data_notouch_zones['selected']=new Array(data_notouch_zones['name'].length).fill(false);
    }
    
    for(let i in data_notouch_zones['name']) {
        // calcul de la couleur du flux
        if(data_notouch_zones['selected'][i]) {
            json_data.data_notouch_zones['color'][i]="rgba(229, 175, 0, 1)";
        } else {
            json_data.data_notouch_zones['color'][i]="rgba(229, 175, 0, 0.5)";
        }
    }
    ds_notouch.data = json_data.data_notouch_zones;
    ds_notouch.change.emit();
}

// disable a flux from the map
function disable_flux(index) {
    if(!json_data.data_flux['selected']) {
        json_data.data_flux['selected']=new Array(json_data.data_flux['name'].length).fill(false);
    }
    noupdate_select=true;
    json_data.data_flux['active'][index]='no';
    load_graph_flux();
    noupdate_select=false;
    update_flux(json_data.data_flux);
}


// restore a flux from the map
function restore_flux(index) {
    if(!json_data.data_flux['selected']) {
        json_data.data_flux['selected']=new Array(json_data.data_flux['name'].length).fill(false);
    }
    noupdate_select=true;
    json_data.data_flux['active'][index]='yes';
    load_graph_flux();
    noupdate_select=false;
    update_flux(json_data.data_flux);
}



// empty_trash
function button_empty_trash() {
    if(!json_data.data_flux['selected']) {
        json_data.data_flux['selected']=new Array(json_data.data_flux['name'].length).fill(false);
    }
    noupdate_select=true;
    
    // splice change the index order in the array, so we procede in reverse order
    $($('#table_trash_flux tbody input').get().reverse()).each(function( index ) {
        idx=$( this ).attr('id').split('_')[1];
        json_data.data_flux['id'].splice(idx,1);
        json_data.data_flux['name'].splice(idx,1);
        json_data.data_flux['hotcold'].splice(idx,1);
        json_data.data_flux['media'].splice(idx,1);
        json_data.data_flux['fclass'].splice(idx,1);
        json_data.data_flux['posX'].splice(idx,1);
        json_data.data_flux['posY'].splice(idx,1);
        json_data.data_flux['posXend'].splice(idx,1);
        json_data.data_flux['posYend'].splice(idx,1);
        json_data.data_flux['color'].splice(idx,1);
        json_data.data_flux['active'].splice(idx,1);
        json_data.data_flux['selected'].splice(idx,1);
    });

    load_graph_flux();
    noupdate_select=false;
    update_flux(json_data.data_flux);
}

// restore_selected
function button_restore_selected() {
    if(!json_data.data_flux['selected']) {
        json_data.data_flux['selected']=new Array(json_data.data_flux['name'].length).fill(false);
    }
    noupdate_select=true;
    $('#table_trash_flux tbody input').each(function( index ) {
        if($( this ).prop('checked')) {
            idx=$( this ).attr('id').split('_')[1];
            json_data.data_flux['active'][idx]='yes';
        }
    });
    load_graph_flux();
    noupdate_select=false;
    update_flux(json_data.data_flux);
}


// removing a flux from the map
function remove_flux(index) {
    if(!json_data.data_flux['selected']) {
        json_data.data_flux['selected']=new Array(json_data.data_flux['name'].length).fill(false);
    }
    if(!confirm('Do you realy want to remove this item?')) return;
    noupdate_select=true;
    json_data.data_flux['id'].splice(index,1);
    json_data.data_flux['name'].splice(index,1);
    json_data.data_flux['hotcold'].splice(index,1);
    json_data.data_flux['media'].splice(index,1);
    json_data.data_flux['fclass'].splice(index,1);
    json_data.data_flux['posX'].splice(index,1);
    json_data.data_flux['posY'].splice(index,1);
    json_data.data_flux['posXend'].splice(index,1);
    json_data.data_flux['posYend'].splice(index,1);
    json_data.data_flux['color'].splice(index,1);
    json_data.data_flux['active'].splice(index,1);
    json_data.data_flux['selected'].splice(index,1);
    load_graph_flux();
    noupdate_select=false;
    update_flux(json_data.data_flux);
}

// removing a zone from the map
function remove_zone(index) {
    if(!json_data.data_notouch_zones['selected']) {
        json_data.data_notouch_zones['selected']=new Array(json_data.data_notouch_zones['name'].length).fill(false);
    }
    if(!confirm('Do you realy want to remove this item?')) return;
    noupdate_select=true;
    json_data.data_notouch_zones['id'].splice(index,1);
    json_data.data_notouch_zones['name'].splice(index,1);
    json_data.data_notouch_zones['x'].splice(index,1);
    json_data.data_notouch_zones['y'].splice(index,1);
    json_data.data_notouch_zones['w'].splice(index,1);
    json_data.data_notouch_zones['h'].splice(index,1);
    json_data.data_notouch_zones['color'].splice(index,1);
    json_data.data_notouch_zones['selected'].splice(index,1);
    load_graph_zones();
    noupdate_select=false;
    update_zones(json_data.data_notouch_zones);
}

//update zone detected
function update_zones(data) {
    if(noupdate_select) return;
    
    if(!data['selected']) {
        data['selected']=new Array(data['name'].length).fill(false);
    }
    //prevent flood
    if(window.timer_floodchanges) {return;}
    window.timer_floodchanges=window.setTimeout(function() {window.timer_floodchanges=false;},500);
    for(i in data['name']) {
        if(data['name'][i]=='init') {
            data['name'][i]='Zone '+(parseInt(i)+1);
        }
        data['color'][i]='rgba(229, 175, 0, 0.5)';
    }
    $.post( "/ajax_setup?action=update_zones", { data: JSON.stringify(data) })
    .done(function( rep ) {
        reload_tables();
    })
    .fail(function() {
        alert( "Connexion error" );
    });
}

// update flux detected
function update_flux(data) {

    if(noupdate_select) return;
    
    if(!data['selected']) {
        data['selected']=new Array(data['name'].length).fill(false);
    }
    
    //prevent flood
    if(window.timer_floodchanges) {return;}
    window.timer_floodchanges=window.setTimeout(function() {window.timer_floodchanges=false;},500);
    
    for(i in data['name']) {
        if(data['color'][i]=='hot') {
            console.log('SALUT')
            data['name'][i]='Flux '+(parseInt(i)+1)+'##';
            data['color'][i]='rgba(255, 0, 0, 0.5)';
            data['media'][i]='';
            data['fclass'][i]='';
            data['selected'][i]='';
            data['active'][i]='yes';
            data['posXend'][i]=10;
            data['posYend'][i]=10;
            data['posX'][i]=20;
            data['posY'][i]=10;
        }
        if(data['hotcold'][i]=='hot') {
            data['color'][i]='rgba(255, 0, 0, 0.5)';
        } else {
            data['color'][i]='rgba(0, 0, 255, 0.5)';
        } 
    }
    console.log(" X "+data['posXend']);
    console.log(" Y "+data['posYend']);
	$.post( "/ajax_setup?action=update_flux", { data: JSON.stringify(data) })
    .done(function( rep ) {
        console.log("UPDATED");
        reload_tables();
    })
    .fail(function() {
        alert( "Connexion error" );
    });
}

// reload left tables
function reload_tables() {
    $.post( "/ajax_setup?action=get_config")
    .done(function( rep ) {
        $('#json_data_index').val(rep);
        load_tables();
    })
    .fail(function() {
        alert( "Connexion error" );
    });
}


//deselect all button
function deselect_all() {
    $('#table_flux tbody input').prop('checked',false);
    $('#table_zones tbody input').prop('checked',false);
    for(let i in json_data.data_flux['selected']) {
        json_data.data_flux['selected'][i]=false;
    }
    for(let i in json_data.data_notouch_zones['selected']) {
        json_data.data_notouch_zones['selected'][i]=false;
    }
    load_graph_zones();
    load_graph_flux(); 
}

//display the modal box to edit a flux
function modal_edit_flux(index) {
    $('#modal_edit_flux').show();
    $('#modal_flux_id').val(index);
    $('#modal_flux_name').val(json_data.data_flux['name'][index]);
    $('#modal_flux_hotcold').val(json_data.data_flux['hotcold'][index]);
    $('#modal_flux_media').val(json_data.data_flux['media'][index]);
    $('#modal_flux_fclass').val(json_data.data_flux['fclass'][index]);
    
    $.get( "/ajax_setup?action=get_tempinout&id="+json_data.data_flux['id'][index])
    .done(function( rep ) {
        rep=JSON.parse(rep);
        $('#modal_flux_tempIn').val(rep['tempIn'].join(' '));
        $('#modal_flux_tempOut').val(rep['tempOut'].join(' '));
    })
    .fail(function() {
        alert( "Connexion error" );
    });
    
}


//function that display checkbox in a dropdown so we can filter by primary/secondary/...
function multiselect_to_dropdown(eleid, multipletext) {
	/* par keul/Michael VOGT (keul.fr) Licence:CreativeCommon0 ( https://codepen.io/keul/pen/bdaGPK )
	param: id of select multiple, text displayed with a 2+ selection */
	if(!multipletext) multipletext='selected';

    var myele = document.getElementById(eleid);
    var opts=myele.options;
    //Don't understand the point of this 
	if(arguments.length==3 && arguments[2]=='blur') {
		clearTimeout(myele.dataset.timer);
        myele.dataset.timer=setTimeout(function(){
			if(document.activeElement.id!=eleid+'_sk_input' && document.activeElement.id!=eleid+'_sk_span') 
				document.getElementById(eleid+'_sk_span').style.display="none";
		},200);
		return;
	}
	if(arguments.length==3 && arguments[2]=='ckbox') {
		var select_qty=0;
		var selectname='';
		for(var i=0,l=opts.length; i<l; i++) {
			myele.options[i].selected=document.getElementById(eleid+'_sk_'+i).checked
			if(document.getElementById(eleid+'_sk_'+i).checked) {
				++select_qty;
				selectname=opts[i].innerHTML;
			}
			if(select_qty>1) {
				document.getElementById(eleid+'_sk_input').value=select_qty+' '+multipletext;
			} else if(select_qty==1) {
				document.getElementById(eleid+'_sk_input').value=selectname.trim();
			} else {
				document.getElementById(eleid+'_sk_input').value='';
			}
		}
        var evt = document.createEvent("HTMLEvents");
        evt.initEvent("change", false, true);
        myele.dispatchEvent(evt);
		return;
	}
	
	var sp2 = document.createElement('input');
	sp2.setAttribute('id', eleid+'_sk_input');
	sp2.setAttribute('type', 'text');
	if(myele.title) {
		sp2.setAttribute('placeholder', myele.title);
	}
	sp2.setAttribute('autocomplete', 'off');
	sp2.setAttribute('readonly', 'readonly');
	sp2.setAttribute('style', 'width:'+myele.offsetWidth+'px');
	sp2.setAttribute('onfocus', 'document.getElementById("'+eleid+'_sk_span").style.display="";');
	sp2.setAttribute('onblur', 'multiselect_to_dropdown(\''+eleid+'\',\''+multipletext+'\',\'blur\');');
	myele.parentNode.insertBefore(sp2, myele.nextSibling);

	var sp3 = document.createElement('span');
    sp3.setAttribute('id', eleid+'_sk_span');
    //Do not understand why this event has to take place here
	//sp3.setAttribute('onmouseout', 'multiselect_to_dropdown(\''+eleid+'\',\''+multipletext+'\',\'blur\');');
	sp3.setAttribute('onclick', 'document.getElementById("'+eleid+'_sk_input").focus();');
	sp3.setAttribute('style', 'min-width:'+sp2.offsetWidth+'px;margin-top:'+sp2.offsetHeight+'px;position:absolute;border:1px solid grey;display:none;z-index:9999;text-align:left;background:white;max-height:130px;overflow-y:auto;overflow-x: hidden;');
	sp2.parentNode.insertBefore(sp3, sp2.nextSibling);

	var tmp='';
	var dis='';
	for(var i=0,l=opts.length; i<l; i++) {
		var slected=(opts[i].selected)?'checked':'';
		dis=myele.disabled?'disabled':'';
		dis=(opts[i].disabled)?'disabled':dis;
		tmp+='<input style="width:1;" type="checkbox" '+slected+' id="'+eleid+'_sk_'+i+'" onchange="multiselect_to_dropdown(\''+eleid+'\',\''+multipletext+'\',\'ckbox\')" '+dis+'><label  style="display:inline;white-space:nowrap;" for="'+eleid+'_sk_'+i+'">'+opts[i].innerHTML+'</label><br>';
	}
	sp3.innerHTML=tmp;
	myele.style.display='none';
	multiselect_to_dropdown(eleid,multipletext,'ckbox');
}