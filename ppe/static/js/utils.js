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
    document.getElementById("mapwidget").style.display =  checkBox.checked ? "block" : "none";
    document.getElementById("validation").style.display =  checkBox.checked ? "inline" : "none";
}

function validateRealEstateNb() {
    // Get the checkbox status
    const selected_nummai = document.getElementById("nummai").value;

    if (selected_nummai != "") {
        document.getElementById("select_bf_info").classList.remove('alert-warning');
        document.getElementById("select_bf_info").classList.add('alert-info');
        document.getElementById("multi_bf").style.display = "inline";
    } else {
        document.getElementById("select_bf_info").classList.remove('alert-info');
        document.getElementById("select_bf_info").classList.add('alert-warning');
        document.getElementById("multi_bf.style").display = "none";
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
        document.getElementById("ref_geoshop").style.display = "block";
    }
    else if (dossier_type == "R"){
        document.getElementById("revision").style.display = "block";
    }
    else if (dossier_type == "M"){
        document.getElementById("modification").style.display = "block";
        document.getElementById("ref_geoshop").style.display = "none";
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
                    document.getElementById("droits_remark").style.display = "none";
                    document.getElementById("situation_cadastrale").style.display = "inline";
                    document.getElementById("constitution").style.display = "none";
                    var ele = document.getElementsByName("elements_rf");
                    for(var j=0;j<ele.length;j++)
                        ele[j].checked = false;
                    }
                else {
                    document.getElementById("droits_remark").style.display = "block";
                    document.getElementById("constitution").style.display = "none";
                    document.getElementById("new_jouissance").style.display = "none";
                    document.getElementById("situation_cadastrale").style.display = "none";
                    document.getElementById("submit_btn").style.display = "none";
                }
            }

        }
    }

function showLayersInfo() {
    // Get the selected radio button
    const situation_plan = document.getElementsByName("situation_plan_rf");

    for (let i=0;i < situation_plan.length; i++) {
        if (situation_plan[i].checked) {
            choix_situation_plan = situation_plan[i].value;
            var ele = document.getElementsByName("layer_info");
            for(var k=0;k<ele.length;k++)
                ele[k].checked = false;
            if (choix_situation_plan == 'non') {
                document.getElementById("constitution").style.display = "block";
                document.getElementById("layer_info").style.display = "none";
            } else {
                document.getElementById("layer_info").style.display = "block";
            }
            document.getElementById("submit_btn").style.display = "block";
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
                for(var j=0;j<ele.length;j++)
                    ele[j].checked = false;
                if (choix_elements_rf == 'non') {
                    document.getElementById("ref_geoshop").style.display = "block";
                    document.getElementById("new_jouissance").style.display = "none";
                } else {
                    document.getElementById("ref_geoshop").style.display = "block";
                    document.getElementById("new_jouissance").style.display = "block";
                }
                document.getElementById("submit_btn").style.display = "block";
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