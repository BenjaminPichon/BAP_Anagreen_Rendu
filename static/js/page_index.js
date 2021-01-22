//look at global.js for the menaing of the variable "noupdate_select"



function index_page() {
	ID_Study_Case_tmp = 0

	$('#etape0_next_step_button').on('click',function() {
		if (ID_Study_Case_tmp != 0){
			localStorage.setItem('ID_Study_Case', ID_Study_Case_tmp);
			$.post( "/ajax_index?action=set_study_case_id",{idsc : ID_Study_Case_tmp})
			.done(function( rep ) {
				console.log(rep);
				window.document.location.href='/setup.html?idsc='+ID_Study_Case_tmp;
				//$("#flux_map").html(rep);
				//rep=JSON.parse(rep);
				//$('#modal_flux_tempIn').val(rep['tempIn'].join(' '));
				//$('#modal_flux_tempOut').val(rep['tempOut'].join(' '));
			})
			.fail(function() {
				alert( "Connexion error" );
			});	
		}
		else{
			alert("You have to select a study case !");
		}
	});

	let case_form = document.querySelector("#new_case_form");
	case_form.addEventListener("submit", function(e) {
			e.preventDefault();
			if (!is_empty(case_form)) {
				var formData = {
					'name'              : $('input[name=casename]').val(),
					'company'           : $('input[name=company_name]').val(),
				};
				$.post("/ajax_index?action=add_new_case", {data : JSON.stringify(formData)})
				.done(function(data) {
					console.log(data);
					location.reload();
				})
				.fail(function(formData) {
					//Handling errors for name
					if (formData.errors.name) {
						$('#nom_cas').addClass('has-errors'); //Add class for errors
						$('#nom_cas').append('<div class="help-block">'+ data.errors.name + '</div>'); //Display the error
					}
					//Handling errors for compagny
					if (formData.errors.company) {
						$('#nom_cas').addClass('has-errors'); //Add class for errors
						$('#nom_cas').append('<div class="help-block">'+ data.errors.company + '</div>'); //Display the error
					}
					else {
						alert("Une erreur est survenue");
					}
				});
			}
			else {
				alert("Veuillez renseigner tous les champs du formulaire")
			}
		},
	);
	/*$('#submit_case').on('click', function() {
		var formData = {
			'name'              : $('input[name=casename]').val(),
			'company'           : $('input[name=company_name]').val(),
		};
		console.log(formData);
		$.post("/ajax_index?action=add_new_case", {data : JSON.stringify(formData)})
		.done(function(rep) {
			console.log(rep);
		})
		.fail(function() {
			alert( "Connexion error" );
		});
	}); */
	
	$('.close').on('click',function() {
		$('#modal_add_case').hide();
	});

	$('#index_add_study_but').on('click',function() {
		$('#modal_add_case').css('display','flex');
	});
	
}

function setTableEvent(){
	console.log("setting table event...");
	$('#fond_param tr').click(function() {
		$(this).find('td div input:radio').prop('checked', true)
		displayPreview($(this).find('#id_case').html())  		
	})
}

function displayPreview(idStudyCase){
	console.log('#prev'+idStudyCase)
	$('.imgPreview').css("display","none")
	$('#prev'+idStudyCase).css("display", "block") 
	ID_Study_Case_tmp = idStudyCase
}


/*No reale function, just an "example"*/
function ajaxExempleNOTtoUSE(){
	$.get( "/ajax_index?action=get_study_case_by_id&id="+idStudyCase)
    .done(function( rep ) {
		 $("#flux_map").html(rep);
        //rep=JSON.parse(rep);
        //$('#modal_flux_tempIn').val(rep['tempIn'].join(' '));
        //$('#modal_flux_tempOut').val(rep['tempOut'].join(' '));
    })
    .fail(function() {
        alert( "Connexion error" );
    });
}