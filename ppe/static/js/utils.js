function resetLocalisation(mode) {
    document.getElementById("id_geom").innerHTML = '';
    const checkBox = document.getElementById("check_mutation");
    const current_action = document.getElementById("localisation_form").getAttribute("action");
    if (mode == 'edit' || current_action == 'ppe/edit_geolocalisation'){
    document.getElementById("localisation_form").action = 'edit_geolocalisation';
    } else {
    document.getElementById("localisation_form").action = 'set_geolocalisation';
    }
 }

function showMap() {
    // Get the checkbox status
    const checkBox = document.getElementById("check_mutation");
    // If the checkbox is checked, display the output text
    mapwidget.style.display =  checkBox.checked ? "block" : "none";
    validation.style.display =  checkBox.checked ? "inline" : "none";
}

function validateRealEstateNb() {
    // Get the checkbox status
    const selected_nummai = document.getElementById("nummai").value;

    if (selected_nummai != "") {
        document.getElementById("select_bf_info").classList.remove('alert-warning');
        document.getElementById("select_bf_info").classList.add('alert-info');
        multi_bf.style.display = "inline";
    } else {
        document.getElementById("select_bf_info").classList.remove('alert-info');
        document.getElementById("select_bf_info").classList.add('alert-warning');
        multi_bf.style.display = "none";
    }
}

function changeSectionDisplay() {
    // Get the selected value
    const dossier_type = document.getElementById("type_dossier").value;

    document.getElementById("submit_btn").style.display = "none";
    document.getElementById("validate_btn").style.display = "none";
    document.getElementById("modification").style.display = "none";
    document.getElementById("constitution").style.display = "none";
    document.getElementById("revision").style.display = "none";
    document.getElementById("ref_geoshop").style.display =  "none";
    if (document.getElementById("form_error")) {
        document.getElementById("form_error").style.display = "none";
    }

    if (dossier_type == "C"){
        document.getElementById("constitution").style.display = "block";
        document.getElementById("ref_geoshop").style.display =  "block";
    }
    else if (dossier_type == "R"){
        document.getElementById("revision").style.display = "block";
    }
    else if (dossier_type == "M"){
        document.getElementById("modification").style.display = "block";
    } 
}

function showJouissanceRemark() {
    // Get the selected radio button
    const droits_jouissance = document.getElementsByName("droits_jouissance");

    if (document.getElementById("form_error")) {
        document.getElementById("form_error").style.display = "none";
    }
    for (let i=0;i < droits_jouissance.length; i++) {
            if (droits_jouissance[i].checked) {
                choix_droits_jouissance = droits_jouissance[i].value;
                if (choix_droits_jouissance == 'non'){
                    droits_remark.style.display = "none";
                    elements_rf.style.display = "block";
                    constitution.style.display = "none";
                    var ele = document.getElementsByName("elements_rf");
                    for(var j=0;j<ele.length;j++)
                        ele[j].checked = false;
                    }
                else {
                    droits_remark.style.display = "block";
                    constitution.style.display = "none";
                    new_jouissance.style.display = "none";
                    elements_rf.style.display = "none";
                    submit_btn.style.display = "none";
                }
            }

        }
    }

function showElementsRFQuestions() {
        // Get the selected radio button
        const elements_rf = document.getElementsByName("elements_rf");
    
        for (let i=0;i < elements_rf.length; i++) {
                if (elements_rf[i].checked) {
                    choix_elements_rf = elements_rf[i].value;
                    var ele = document.getElementsByName("new_jouissance");
                    for(var k=0;k<ele.length;k++)
                        ele[k].checked = false;
                    if (choix_elements_rf == 'non') {
                        constitution.style.display = "block";
                        ref_geoshop.style.display = "inline";
                        new_jouissance.style.display = "none";
                    } else {
                        new_jouissance.style.display = "block";
                        constitution.style.display = "none";
                        ref_geoshop.style.display = "none";
                    }
                    submit_btn.style.display = "block";
                }
    
            }
        }

function showSubmitButton() {
    submit_btn.style.display = "inline";
}

 function showValidateButton() {
    if (document.getElementById("form_error")) {
        document.getElementById("form_error").style.display = "none";
    }
    validate_btn.style.display = "inline";
}

function openBottle() {
    go_champagne.style.display = "none";
    champagne.style.display = "inline";
}