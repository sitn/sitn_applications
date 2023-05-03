document.getElementById("nav-saisie-tab").onclick = () => {
  if (ph.activecadastre !== null) {
    document.getElementById("step1").style.display = "block";
    document.getElementById("step2").style.display = "none";
  } else {
    document.getElementById("cadastre_selector").style.display = "block";
    document.getElementById("nav-listing-tab").classList.add("disabled");
    document.getElementById("nav-control-tab").classList.add("disabled");
  }
}

document.getElementById("plan_list").onchange = () => {
  const val = document.getElementById("plan_list").value;
  document.getElementById("desgn_list").value = val;
}

document.getElementById("desgn_list").onchange = () => {
  const val = document.getElementById("desgn_list").value;
  document.getElementById("plan_list").value = val;
}

document.getElementById("close-saisie").onclick = () => {
  const text = "Êtes-vous sûr de vouloir quitter la saisie?\nTous les éléments saisis seront perdus";
  if (confirm(text) == true) {
    document.getElementById("step1").style.display = "none";
    document.getElementById("cadastre_selector").style.display = "block";
    ph.activecadastre=null;
    document.getElementById("nav-listing-tab").classList.add("disabled");
    document.getElementById("nav-control-tab").classList.add("disabled");
    // Reset form
    document.getElementById("delayed_check").checked = false;
    document.getElementById("div_check").checked = false;
    document.getElementById("cad_check").checked = false;
    document.getElementById("serv_check").checked = false;
    document.getElementById("art35_check").checked = false;
    document.getElementById("other_check").checked = false;
    document.getElementById("complement").value = "";
  }
}

document.getElementById("load-desgn").onclick = () => {
  const id = document.getElementById("desgn_list").value;
  ph.get_download_path(id, 'designation');
}


document.getElementById("load-plan").onclick = () => {
  const id = document.getElementById("plan_list").value;
  ph.get_download_path(id, 'plan');
}

document.getElementById("nav-listing-tab").onclick = () => {
  document.getElementById("step1").style.display = "none";
  document.getElementById("step2").style.display = "none";
};

document.getElementById("nav-control-tab").onclick = () => {
  document.getElementById("step1").style.display = "none";
  document.getElementById("step2").style.display = "none";
};
/*
document.getElementById("saisie-tab").onclick = () => {
  document.getElementById("saisie-tab").classList.add("active");
  document.getElementById("control_section").classList.remove("active");
  document.getElementById("saisie-tab-pane").style.display = "block";
};
*/
ph = {
  activecadastre: null,
  cadastres: {},
};

ph.initApplication = function() {
  // Token is needed for calling Django using POST
  ph.csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  ph.load_cadastre();
  console.log('paf')
};

// Gets the list of cadastre (application entry point)
ph.load_cadastre = () => {
  const select = document.getElementById("cadastre_list");
  let i, L = select.options.length - 1;
  for(i = L; i >= 0; i--) {
    select.remove(i);
  }
  fetch("../cadastre/get")
  .then((response) => response.json())
  .then((data) => {  
    for (let i = 0; i < data.length; i++){
      let item = data[i];
      let element = document.createElement("option");
      ph.cadastres[item["numcad"]] = item["cadnom"];
      element.innerText = item["cadnom"];
      element.value = item["numcad"];
      select.append(element);
      document.getElementById("overlay").style.display = "none";
   //   document.getElementById("control_section").classList.add("disabled");
      document.getElementById("cadastre_selector").style.display = "block";
    }        
  });
};

// Choosing a cadastre sends user to step 1 display
document.getElementById("choose_cadastre").onclick = () => {

  document.getElementById("overlay").style.display = "block";
  const e = document.getElementById("cadastre_list");
  const selected_value = e.options[e.selectedIndex].value;
  const url = "get_docs_list?" + new URLSearchParams({
    numcad: selected_value
  });
  fetch(url)
    .then((response) => response.json())
    .then((data) => {
      let item; let element;
      const plan_list = document.getElementById("plan_list");
      const desgn_list = document.getElementById("desgn_list");
      const list = data['list'];
      for (let i = 0; i < list.length; i++){
        item = list[i];
        element = document.createElement("option");
        element.innerText = item["link"];
        element.value = item["id"];
        plan_list.append(element);
        element = document.createElement("option");
        element.value = item["id"];
        if (item['designation_id'] !== null) {
          element.innerText = item["link"];
        } else {
          element.innerText = "-";
        }
        desgn_list.append(element);
      }
      ph.activecadastre = document.getElementById("cadastre_list").value;
      document.getElementById("cadastre_selector").style.display = "none";
      document.getElementById("step1").style.display = "block";
      const cadastre_text_tags = document.querySelectorAll(".cadastre_text");
      for (let i = 0; i < cadastre_text_tags.length; i++) {
        cadastre_text_tags[i].innerText = ph.cadastres[ph.activecadastre];
      }
      document.getElementById("overlay").style.display = "none";
      document.getElementById("nav-listing-tab").classList.remove("disabled");
      document.getElementById("nav-control-tab").classList.remove("disabled");

      const download_path = data['download'];
      
    // The most recent document is automatically opened, might it be a plan or a designation
    // (currently commented because of development purposes)
    /*  
     ph.get_document(download_path)
    */
  });
};

// The download path is the direct access to documents (plans or designation)
// They are fetched on the fly when needed
ph.get_download_path = (id, type) => {;
  const url = "get_download_path?" + new URLSearchParams({
    id: id,
    type: type
  });
  fetch(url)
    .then((response) => response.json())
    .then((data) => {
      ph.get_document(data["download_path"]);
  });
};

// Using the download path (which is fetch using the upper function),
// a document can be fetched.
ph.get_document = (download_path) => {
  const download_file = download_path.split('/').at(-1);
  fetch('download/'+download_path)
  .then(res => res.blob())
  .then(data => {
    let a = document.createElement("a");
    a.href = window.URL.createObjectURL(data);
    a.download = download_file;
    a.click();
    window.URL.revokeObjectURL('download/'+download_path);
  });
};

// Submitting data from the step 1 form.
document.getElementById("submit-form").onclick = () => {

  document.getElementById("overlay").style.display = "block";

  const delayed_check = document.getElementById("delayed_check").checked

  const params = {
    id: document.getElementById("plan_list").value,
    div_check: document.getElementById("div_check").checked,
    cad_check: document.getElementById("cad_check").checked,
    serv_check: document.getElementById("serv_check").checked,
    art35_check: document.getElementById("art35_check").checked,
    other_check: document.getElementById("other_check").checked,
    delayed_check: delayed_check,
    complement: document.getElementById("complement").value,
  };


  // A delayed plan can only be delayed, nothing else can be done
  if (delayed_check === true) {
    let text = "Une désignation ou un plan retardé ne permet pas d'enregistrer d'autres informations";
    text += "\n\nSeul le retard est enregistré. De plus, il faudra procéder via l'interface de contrôle."
    if (confirm(text) == false) {
      return;
    }
  }

  // submitting with the token because Django needs it when doing a POST request
  fetch('submit_saisie', {
    method: 'POST',
    headers: {
      'Accept': 'application/json, text/plain,  */*',
      'Content-Type': 'application/json'
    },
    headers: {'X-CSRFToken': ph.csrftoken},
    mode: 'same-origin',
    body: JSON.stringify(params),
  })
  .then(res => res.json())
  .then(res => {
    ph.resetSubmitForm(res['has_div']);
  });  
};

// Data submission was sucessfull: resetting form and opening balance interface (if is is a division)
ph.resetSubmitForm = (div) => {
  // Open div panel (if div)
  document.getElementById("step1").style.display = "none";
  if (div === true) {
    document.getElementById("step2").style.display = "block";
    document.getElementById("overlay").style.display = "none";
  } else {
    ph.load_cadastre();
  }
  // reset saisie form
  document.getElementById("delayed_check").checked = false;
  document.getElementById("div_check").checked = false;
  document.getElementById("cad_check").checked = false;
  document.getElementById("serv_check").checked = false;
  document.getElementById("art35_check").checked = false;
  document.getElementById("other_check").checked = false;
  document.getElementById("complement").value = "";

};




// https://www.raymondcamden.com/2022/03/14/building-table-sorting-and-pagination-in-javascript