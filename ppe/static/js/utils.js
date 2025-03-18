function showMap() {
    // Get the checkbox
    const checkBox = document.getElementById("check_mutation");
    // Get the output text
    const carte = document.getElementById("mapwidget");

    // If the checkbox is checked, display the output text
    mapwidget.style.display =  checkBox.checked ? "block" : "none";
}
