
cats = {};

function pickHex(color1, color2, weight) {
    var w1 = weight;
    var w2 = 1 - w1;
    var rgb = [Math.round(color1[0] * w1 + color2[0] * w2),
        Math.round(color1[1] * w1 + color2[1] * w2),
        Math.round(color1[2] * w1 + color2[2] * w2)];
    return rgb;
}

var color1 = '305170';
var color2 = '6DFC6B';
var ratio = 0.5;

var hex = function(x) {
    x = x.toString(16);
    return (x.length == 1) ? '0' + x : x;
};



function init() {
    $('#catsTable').DataTable( {
        searching: false,
        paging: false,
        info: false,
        ajax: {
            url: cats.get_activity_url
        },
        initComplete: function () {
            let api = this.api();
            const data = api.ajax.json();
            const max = data.max;
            const min = data.min;
            
            api.columns(':not(:first)').every(function () {
                let ratio, r, g, b;
                api.cells(':not(:first)').every(function () {
                    if (this.node().innerText !== '0' && this.node().innerText !== null) {
                        ratio = parseFloat(this.node().innerText) / (max-min);
                        r = Math.ceil(parseInt(color1.substring(0,2), 16) * ratio + parseInt(color2.substring(0,2), 16) * (1-ratio));
                        g = Math.ceil(parseInt(color1.substring(2,4), 16) * ratio + parseInt(color2.substring(2,4), 16) * (1-ratio));
                        b = Math.ceil(parseInt(color1.substring(4,6), 16) * ratio + parseInt(color2.substring(4,6), 16) * (1-ratio));
                        $(this.node()).css("background-color", "rgb("+r+", "+g+", "+b+", 0.6)");
                    }
                });
            });
        },
        columnDefs: [{
            targets: [1, 2, 3, 4],
            render: function (data) {
                return data === 0 ? null : data;
            }
        }],
    } );
};
