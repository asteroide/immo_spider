
function showDialog() {
    $( "#toggle" ).show();
    $( "#info" ).tabs();
    $( "#info" ).dialog();
}

var raster = new ol.layer.Tile({
    title: "Immo Spider",
    source: new ol.source.OSM()
});

var vector = new ol.layer.Vector({
    title: 'Houses',
    source: new ol.source.Vector({
        url: 'http://127.0.0.1:8080/api/features',
        format: new ol.format.GeoJSON()
    },
    {
        //tileOptions: {crossOriginKeyword: 'anonymous'},
        transitionEffect: null
    }),
    style: new ol.style.Style({
        image: new ol.style.Circle({
            radius: 5,
            fill: new ol.style.Fill({
                color: '#0000FF'
            }),
            stroke: new ol.style.Stroke({
                color: '#000000'
            })
        })
    })
});

var map = new ol.Map({
    interactions: ol.interaction.defaults().extend([
        new ol.interaction.Select({
            style: selectAD
        })
    ]),
    target: 'map',
    layers: [raster, vector],
    view: new ol.View({
        center: ol.proj.fromLonLat([-2.8185137, 47.6577568]),
        zoom: 10
    }),
    controls: ol.control.defaults({
        attributionOptions: {
            collapsible: true
        }
    }),
    controls: ol.control.defaults().extend([
        new ol.control.ScaleLine()
    ])
});

var infoList;

function updateInfo(data_index) {
    var data = infoList[data_index];
    var infoElement1 = document.getElementById('tabs-1-content');
    var infoElement2 = document.getElementById('tabs-2-content');
    var infoElement3 = document.getElementById('tabs-3-content');
    var infoElement4 = document.getElementById('tabs-4-content');
    infoElement1.innerHTML =
        '<h1>'+data["address"]+'</h1>'+data["description"]+ '<br>' +
            '<a href="'+data["url"]+'" target="_blank">link to the ad</a>';
    infoElement2.innerHTML =
        'TODO';
    infoElement3.innerHTML =
            'surface : ' + data["surface"] + "<br/>" +
            'jardin : ' + data["groundsurface"] + "<br/>" +
            'prix : ' + data["price"] + "<br/>" +
            'date : ' + data["date"] + "<br/>";
    infoElement4.innerHTML =
        'TODO'
    ;
}

function selectAD(feature) {
    var infolink = document.getElementById('info-link');
    $.getJSON('http://127.0.0.1:8080/api/data?geoid='+feature['i'],
        function(data_list) {
            //var data = data_list[0];
            infoList = data_list;
            if (data_list.length > 1) {
                infolink.innerHTML = "";
                for (var i=0 ; i<data_list.length ; i++) {
                    //console.log('<a href="#" onclick="updateInfo('+JSON.stringify(data_list[i])+')">annonce '+i+'</a> ');
                    var json_str = JSON.stringify(data_list[i]);
                    infolink.innerHTML += '<a href="#" onclick="updateInfo('+i+')">annonce '+i+'</a> ';
                }
                //console.log(infolink.innerHTML);
            }
            else {
                infolink.innerHTML = "";
            }
            updateInfo(0);
        });
    showDialog();
    return new ol.style.Style({
        image: new ol.style.Circle({
            radius: 5,
            fill: new ol.style.Fill({
                color: '#00FF00'
            }),
            stroke: new ol.style.Stroke({
                color: '#000000'
            })
        })
    })
}
