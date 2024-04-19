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
    ph.activecadastre = null;
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
  ph.load_table();
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

document.getElementById("load-infolica").onclick = () => {
  const no_infolica = document.getElementById("no_infolica").value;
  ph.getBalance(no_infolica);
};

document.getElementById("balance-add-old-bf").onclick = () => {
  let balance_old_bf = document.getElementById("balance-old-bf").value;
  const balance_old_bf_serie = Number(document.getElementById("balance-old-bf-serie").value);

  if (!balance_old_bf && typeof balance_old_bf !== 'number') {
    return;
  }
  balance_old_bf = Number(balance_old_bf);

  let tableau_balance = document.getElementById('tableau_balance').firstChild;
  let nb_rows;
  const nb_cols = tableau_balance.rows[0].cells.length;

  let cadastre_id = 14;

  for (let j = 0; j < balance_old_bf_serie; j++) {
    nb_rows = tableau_balance.rows.length;

    let row = tableau_balance.insertRow(-1)
    let cell = row.insertCell(0)

    cell.outerHTML = '<td style="text-align: center; padding: 5pt; border: solid 1pt black">' + cadastre_id + '_' + balance_old_bf + ` <a href="javascript:balance_removeBF('${cadastre_id}_${balance_old_bf}')" title="supprimer le bien-fonds">[-]</a></td>`;

    for (let i = 1; i < nb_cols; i++) {
      cell = row.insertCell(i)
      cell.outerHTML = '<td style="text-align: center; padding: 5pt; border: solid 1pt black"><input type="checkbox" id="' + cadastre_id + '_' + balance_old_bf + '-' + tableau_balance.rows[0].cells[i].innerHTML.split(' ')[0] + '"></input></td>';
    }

    balance_old_bf += 1;

  }

  document.getElementById("balance-old-bf").value = '';
  document.getElementById("balance-old-bf-serie").value = 1;
};

document.getElementById("balance-add-new-bf").onclick = () => {
  let balance_new_bf = document.getElementById("balance-new-bf").value;
  const balance_new_bf_serie = Number(document.getElementById("balance-new-bf-serie").value);

  if (!balance_new_bf && typeof balance_new_bf !== 'number') {
    return;
  }

  balance_new_bf = Number(balance_new_bf);

  let tableau_balance = document.getElementById('tableau_balance').firstChild;
  const nb_rows = tableau_balance.rows.length;
  let nb_cols;

  let cadastre_id = 14;

  for (let j = 0; j < balance_new_bf_serie; j++) {
    nb_cols = tableau_balance.rows[0].cells.length;

    let cell = tableau_balance.rows[0].insertCell(-1)

    cell.outerHTML = '<td style="text-align: center; padding: 5pt; border: solid 1pt black">' + cadastre_id + '_' + balance_new_bf + ` <a href="javascript:balance_removeBF('${cadastre_id}_${balance_new_bf}')" title="supprimer le bien-fonds">[-]</a></td>`;

    for (let i = 1; i < nb_rows; i++) {
      cell = tableau_balance.rows[i].insertCell(-1)
      cell.outerHTML = '<td style="text-align: center; padding: 5pt; border: solid 1pt black"><input type="checkbox" id="' + tableau_balance.rows[i].cells[0].innerHTML.split(' ')[0] + '-' + cadastre_id + '_' + balance_new_bf + '"></input></td>';
    }

    balance_new_bf += 1;
  }

  document.getElementById("balance-new-bf").value = '';
  document.getElementById("balance-new-bf-serie").value = 1;
};

// submit-balance
document.getElementById("submit-balance").onclick = () => {
  // get relations
  const relations = getBalanceRelations();
  if (relations.length === 0) {
    return;
  }

  // post relations
  postBalanceRelation(relations);

  // hide balance sections
  // document.getElementById("balance-add-bf-section").style.display = 'none';
  // document.getElementById("tableau_balance").innerHTML = '';

}

function handleEnterAsClick(e, elementId) {
  if (e.keyCode === 13) {
    e.preventDefault();
    document.getElementById(elementId).click();
  }
}

function getBalanceRelations() {
  let relations = new Array();

  const tableau_balance = document.getElementById('tableau_balance').firstChild;

  const nb_rows = tableau_balance.rows.length
  const nb_cols = tableau_balance.rows[0].cells.length

  // get all old_bf
  let old_bf = new Array()
  for (let i = 1; i < nb_rows; i++) {
    old_bf.push(tableau_balance.rows[i].cells[0].innerHTML);
  }

  // get all new_bf
  let new_bf = new Array()
  for (let i = 1; i < nb_cols; i++) {
    new_bf.push(tableau_balance.rows[0].cells[i].innerHTML);
  }

  async function postBalanceRelation(relations) {
    console.log(`postBalanceRelation | still to do`)
    console.log(`post(...)`)
    console.log(`relations`, relations)
  }

  // get all relations
  let id_rel = '';
  for (obf of old_bf) {
    for (nbf of new_bf) {
      id_rel = [obf, nbf].join("-");
      if (document.getElementById(id_rel).checked === true) {
        relations.push(id_rel);
      }
    }
  }

  return relations;
}

ph = {
  activecadastre: null,
  cadastres: {},
};

ph.initApplication = function () {
  // Token is needed for calling Django using POST
  ph.csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  ph.load_cadastre();
};

// Gets the list of cadastre (application entry point)
ph.load_cadastre = () => {
  const select = document.getElementById("cadastre_list");
  let i, L = select.options.length - 1;
  for (i = L; i >= 0; i--) {
    select.remove(i);
  }
  fetch("../cadastre/get")
    .then((response) => response.json())
    .then((data) => {
      for (let i = 0; i < data.length; i++) {
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
      for (let i = 0; i < list.length; i++) {
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
ph.get_download_path = (id, type) => {
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
  fetch('download/' + download_path)
    .then(res => res.blob())
    .then(data => {
      let a = document.createElement("a");
      a.href = window.URL.createObjectURL(data);
      a.download = download_file;
      a.click();
      window.URL.revokeObjectURL('download/' + download_path);
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
    headers: { 'X-CSRFToken': ph.csrftoken },
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

    ph.showBalance();
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

// Global table showing all records for a given cadastre
// Two action buttons enable to show details or to change the
// plan/designation status.
ph.load_table = () => {
  document.getElementById("overlay").style.display = "block";

  const url = "api/plans?" + new URLSearchParams({
    numcad: ph.activecadastre,
    format: 'json'
  });

  const grid = new gridjs.Grid({
    columns: [
      'N° plan',
      {
        name: 'Designation',
        formatter: (cell) => cell ? cell.replace('.pdf', '') : null
      },
      'État',
      'Date plan',
      {
        name: 'Actions',
        sort: false,
        formatter: (cell, row) => {
          // Should be set to "done" value (currently not the good value -> developping)
          if (row.cells[2].data === 'A faire') {
            return new gridjs.h('button', {
              className: 'btn btn-secondary',
              onClick: () => ph.changeStatus(row.cells[4].data, 'free')
            }, 'Libérer');
          }
        },
      },
      {
        name: 'Détails',
        sort: false,
        formatter: (cell, row) => {
          // Should be set to "done" value (currently not the good value -> developping)
          if (row.cells[2].data === 'A faire') {
            return new gridjs.h('button', {
              className: 'btn btn-secondary',
              onClick: () => ph.showBalance(row.cells[4].data)
            }, 'Détails');
          }
        },
      },
    ],
    server: {
      url: url,
      then: (data) => data.results.map(plan =>
        [
          plan.plan_number,
          plan.designation,
          plan.state,
          plan.date_plan,
          plan.id,
          plan.id
        ]
      ),
      total: data => data.count,
    },
    pagination: {
      limit: 20,
      server: {
        url: (prev, page) => {
          page += 1;
          return `${prev}&page=${page}`;
        }
      }
    },
    sort: {
      multiColumn: false,
      server: {
        url: (prev, columns) => {
          if (!columns.length) return prev;
          const column_names = [
            'plan',
            'designation',
            'state',
            'date_plan',
          ];
          const col = columns[0];
          const dir = col.direction === 1 ? '' : '-';
          let colName = column_names[col.index];
          return `${prev}&ordering=${dir}${colName}`;
        }
      }
    },
    search: {
      server: {
        url: (prev, keyword) => `${prev}?search=${keyword}`
      }
    },
    language: {
      'search': {
        'placeholder': 'Rechercher...'
      },
      'pagination': {
        'previous': 'Précédent',
        'next': 'Suivant',
        'showing': 'Affichage de l\'élément',
        'to': 'à',
        'of': 'sur',
        'results': 'éléments'
      }
    }
  });
  grid.render(document.getElementById("plan-list-table"));
  document.getElementById("overlay").style.display = "none";
};


ph.getBalance = (id) => {
  fetch(ph.infolica_api_url + 'balance_from_affaire_id?' + new URLSearchParams({
    division_id: id,
    cadastre_id: ph.activecadastre
  })
  )
    .then((response) => response.json())
    .then((data) => {
      if (!Object.keys(data).includes('balance')) {
        document.getElementById("tableau_balance").innerHTML = '<p><em>(' + data.error.detail + ')</em></p>';
        return;
      }

      let balance = data.balance;

      if (balance === null) {
        document.getElementById("tableau_balance").innerHTML = '<p>Aucune balance</p>';
        return;
      }

      let tb_html = '<table style="border: solid 1pt black">'
      for (let i = 0; i < balance.length; i++) {
        tb_html += '<tr>';
        for (let j = 0; j < balance[0].length; j++) {
          if (i > 0 && j > 0) {
            tb_html += '<td style="text-align: center; padding: 5pt; border: solid 1pt black">' +
              '<input type="checkbox" id="' + balance[i][j].id + '" ' + (balance[i][j].state ? 'checked' : '') + '></input>' +
              '</td>';
          } else {
            tb_html += '<td style="text-align: center; padding: 5pt; border: solid 1pt black">' + (balance[i][j] ? balance[i][j] + ((i!==0 ^ j!==0) ? ` <a href="javascript:balance_removeBF('${balance[i][j]}')" title="supprimer le bien-fonds">[-]</a>`: '') : '') + '</td>';
          }
        }
        tb_html += '</tr>';
      }
      tb_html += '</table>';

      document.getElementById("tableau_balance").innerHTML = tb_html;
      document.getElementById("balance-add-bf-section").style.display = "block";

    }).catch((err) => {
      alert('Une erreur s\'est produite. Veuillez contacter l\'administrateur\n\n \
      Détail de l\'erreur:\n' + String(err));
    });

  return;
};

balance_removeBF = (bf) => {

  let table = document.getElementById("tableau_balance").children[0];
  let row_idx=0;
  let col_idx=0;

  for (let row of table.rows) {
    if (row_idx === 0) {
      for (let col of row.cells) {
        if (col.innerText.split(' ')[0] === (bf)) {

          // remove column
          for (let j = 0; j < table.rows.length; j++) {
            table.rows[j].deleteCell(col_idx);
          }

          return;
        }
        col_idx += 1;
      }
    } else {
      if (row.cells[0].innerText.split(' ')[0] === (bf)) {

        // remove row
        document.getElementById("tableau_balance").children[0].deleteRow(row_idx);

        return;
      }
    }
    row_idx += 1;
  }
}


ph.showBalance = (id) => {
  // TODO
  console.log(`Balance "${id}"`);
};

ph.changeStatus = (id, type) => {
  //TODO
  console.log(`Change status to "${type}" for "${id}"`);
};