function changeLocalisationFormAction() {
    // Get the current action
    document.getElementById("localisation_form").action = "/ppe/geolocalisation";
    document.getElementById("localisation_form").submit()
}

function changeOverviewFormAction() {
    // Get the current action
    document.getElementById("overview_form").action = "/ppe/modification";
    document.getElementById("overview_form").submit()
}

function showMap() {
    // Get the checkbox
    const checkBox = document.getElementById("check_mutation");
    // Get the output text
    const carte = document.getElementById("mapwidget");

    // If the checkbox is checked, display the output text
    mapwidget.style.display =  checkBox.checked ? "block" : "none";
    localisation_overview.style.display =  checkBox.checked ? "block" : "none";
}

function changeSectionDisplay() {
    // Get the selected value
    const dossier_type = document.getElementById("type_dossier").value;

    if (dossier_type == ""){
        submit_btn.style.display = "none";
        modification.style.display = "none";
        constitution.style.display = "none";
        revision.style.display = "none";
    }
    else if (dossier_type == "C"){
        submit_btn.style.display = "none";
        modification.style.display = "none";
        constitution.style.display = "block";
        revision.style.display = "none";
    }
    else if (dossier_type == "R"){
        submit_btn.style.display = "none";
        modification.style.display = "none";
        constitution.style.display = "none";
        revision.style.display = "block";
    }
    else {
        modification.style.display = "block";
        constitution.style.display = "none";
        submit_btn.style.display = "none";
        revision.style.display = "none";
    }
}

function showJouissanceRemark() {
    // Get the selected radio button
    const droits_jouissance = document.getElementsByName("droits_jouissance");

    for (let i=0;i < droits_jouissance.length; i++) {
            if (droits_jouissance[i].checked) {
                choix_droits_jouissance = droits_jouissance[i].value;
                droits_remark.style.display = (choix_droits_jouissance == 'oui') ? "block" : "none";
                elements_rf.style.display = (choix_droits_jouissance == 'oui') ? "none" : "block";
                if (choix_droits_jouissance == 'oui') {
                    new_jouissance.style.display = "none";
                    no_plan_remark.style.display = "none";
                    jouissance_remark.style.display = "none";
                    document.getElementsByName("elements_rf")[0].value = false;
                    document.getElementsByName("elements_rf")[1].value = false;
                }
                submit_btn.style.display = "block";
            }

        }
    }

function showElementsRFQuestions() {
        // Get the selected radio button
        const elements_rf = document.getElementsByName("elements_rf");
    
        for (let i=0;i < elements_rf.length; i++) {
                if (elements_rf[i].checked) {
                    choix_elements_rf = elements_rf[i].value;
                    new_jouissance.style.display = (choix_elements_rf == 'oui') ? "block" : "none";
                    if (choix_elements_rf == 'non') {
                        no_plan_remark.style.display = "none";
                        jouissance_remark.style.display = "none";
                        document.getElementsByName("new_jouissance")[0].value = false;
                        document.getElementsByName("new_jouissance")[1].value = false;
                    }
                    submit_btn.style.display = "block";
                }
    
            }
        }

function showNewJouissanceInfo() {
        // Get the selected radio button
        const new_jouissance = document.getElementsByName("new_jouissance");

        for (let i=0;i < new_jouissance.length; i++) {
                if (new_jouissance[i].checked) {
                    choix_new_jouissance = new_jouissance[i].value;
                    no_plan_remark.style.display = (choix_new_jouissance == 'oui') ? "block" : "none";
                    jouissance_remark.style.display = (choix_new_jouissance == 'oui') ? "none" : "block";
                    submit_btn.style.display = "block";
                }
    
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
