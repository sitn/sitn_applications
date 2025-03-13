function showMap() {
// Get the checkbox
var checkBox = document.getElementById("check_mutation");
// Get the output text
var carte = document.getElementById("mapwidget");

// If the checkbox is checked, display the output text
if (checkBox.checked == true){
    mapwidget.style.display = "block";
} else {
    mapwidget.style.display = "none";
}
}