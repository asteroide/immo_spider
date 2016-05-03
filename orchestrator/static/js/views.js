
var feature_colors = new Array();

function showDialog() {
    $( "#toggle" ).show();
    $( "#info" ).tabs();
    $( "#info" ).dialog();
}

function selectAD(feature) {
    var infolink = document.getElementById('info-link');
    $.getJSON('/api/data?geoid='+feature['i'],
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
    var color = "#0000FF";
    $.ajax({
        'async': false,
        'type': "POST",
        'global': false,
        'url': '/api/data?geoid='+feature['i'],
        'success': function (data) {
            color = data[0].color;
            //feature.style.color = color;
        }
    });
    //feature_colors.append(feature['i'],color);
    return new ol.style.Style({
                image: new ol.style.Circle({
                    radius: 5,
                    fill: new ol.style.Fill({
                        color: color
                    }),
                    stroke: new ol.style.Stroke({
                        color: '#000000'
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
        // tileOptions: {crossOriginKeyword: 'anonymous'},
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

function  hide_add() {
    $.getJSON('/api/data?geoid='+feature['i']+'&action=hide',
        function(data_list) {
            document.reload();
        });
}

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
        "<div class='right'><a href='#' onclick='hide_add()' class='button'>Cacher</a></div>"
    ;
}

//map_interaction = new ol.interaction.defaults().extend([
//        ol.interaction.Select({
//            style: selectAD
//        })]);
//
//map.addInteraction(map_interaction);

//console.log(feature_colors);
//
//vector.getSource().once('change',function(e) {
//    if (vector.getSource().getState() === 'ready') {
//        vector.getSource().forEachFeature(function (feature) {
//                //var id = feature.get('i');
//                //console.log("forEachFeature: " + feature_colors[feature.i]);
//                feature.setStyle(new ol.style.Style({
//                    image: new ol.style.Circle({
//                        radius: 5,
//                        fill: new ol.style.Fill({
//                            color: '#003344'
//                        }),
//                        stroke: new ol.style.Stroke({
//                            color: '#000000'
//                        })
//                    })
//                }));
//            }
//        );
//    }
//});
//
//
////vectorSource.forEachFeature(function (feature) {
////        var id = feature.get('i');
////        console.log("forEachFeature: " + id);
////    });
//
//console.log("after forEachFeature");
