function changeFormAction() {
    // Get the current action
    document.getElementById("localisation_form").action = "/ppe/geolocalisation";
    document.getElementById("localisation_form").submit()
}

function showMap() {
    // Get the checkbox
    const checkBox = document.getElementById("check_mutation");
    // Get the output text
    const carte = document.getElementById("mapwidget");

    // If the checkbox is checked, display the output text
    mapwidget.style.display =  checkBox.checked ? "block" : "none";
}

function showSituationBatiments() {
    // Get the selected value
    const dossier_type = document.getElementById("type_dossier").value;

    if (dossier_type == ""){
        submit_btn.style.display = "none";
        type_modification.style.display = "none";
        type_constitution.style.display = "none";
    }
    else if (dossier_type == "C"){
        submit_btn.style.display = "none";
        type_modification.style.display = "none";
        type_constitution.style.display = "block";
    }
    else {
        type_modification.style.display = "block";
        type_constitution.style.display = "none";
        submit_btn.style.display = "block";
    }
}

function showRefGeoshop() {
    // Get the selected radio button
    const situtation_bati = document.getElementsByName("situation_bati");

    for (let i=0;i < situtation_bati.length; i++) {
            if (situtation_bati[i].checked) {
                choix_situation_bati = situtation_bati[i].value;
                ref_geoshop.style.display = (choix_situation_bati == 'nouveau_batiment') ? "block" : "none";
                submit_btn.style.display = "block";
            }

        }
    }
