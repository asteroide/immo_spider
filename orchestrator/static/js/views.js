var infoData = {};

function showDialog() {
    $( "#toggle" ).show();
    $( "#info" ).tabs();
    $( "#info" ).dialog();
}

function selectAD(feature) {
    var infolink = document.getElementById('info-link');
    var info_key;
    $.getJSON('/api/data?geoid='+feature['i'],
        function(data_list) {
            if (data_list.length > 1) {
                infolink.innerHTML = "";
                for (var i=0 ; i<data_list.length ; i++) {
                    info_key = feature['i'] + "_" + i;
                    infolink.innerHTML += '<a href="#" onclick="updateInfo('+info_key+')">annonce '+i+'</a> ';
                    infoData[info_key] = data_list[i];
                }
            }
            else {
                infolink.innerHTML = "";
                info_key = feature['i'] + "_0";
                infoData[info_key] = data_list[0];
            }
            info_key = feature['i'] + "_0";
            updateInfo(info_key);
        });
    showDialog();
    return new ol.style.Style({
        image: new ol.style.Circle({
            radius: 10,
            fill: new ol.style.Fill({
                color: '#FFFFFF'
            }),
            stroke: new ol.style.Stroke({
                color: '#FF0000'
            })
        })
    })
}

function getColoredPoint(feature, resolution) {
    var color = "#bbbbbb";
    var stroke = "#000000";
    $.ajax({
        'async': false,
        'type': "POST",
        'global': false,
        'url': '/api/data?geoid='+feature['i'],
        'success': function (data) {
            if (data.length > 0) {
                color = data[0].color;
                for (var cpt = 0 ; cpt++ ; cpt<data.length) {
                    infoData[feature['i'] + "_" + cpt] = null;
                }
            }
            else {
                stroke = "#bbbbbb";
            }
        }
    });
    return new ol.style.Style({
                image: new ol.style.Circle({
                    radius: 5,
                    fill: new ol.style.Fill({
                        color: color
                    }),
                    stroke: new ol.style.Stroke({
                        color: stroke
                    })
                })
            });
}

var raster = new ol.layer.Tile({
    title: "Immo Spider",
    source: new ol.source.OSM()
});

var vectorSource = new ol.source.Vector({
        url: '/api/features',
        format: new ol.format.GeoJSON()
    },
    {
        transitionEffect: null
    });

var vector = new ol.layer.Vector({
    title: 'Houses',
    source: vectorSource,
    style: getColoredPoint
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

function  hide_ad(uuid) {
    $.getJSON('/api/data?uuid='+uuid+'&action=hide',
        function(data_list) {
            location.reload();
        });
}

function updateInfo(data_uuid) {
    var data = infoData[data_uuid];
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
        "<div class='right'><a href='#' onclick='hide_ad(\""+data["id"]+"\")' class='button'>Cacher</a></div>"
    ;
}
