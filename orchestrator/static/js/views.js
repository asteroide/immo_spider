
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

function selectAD(feature) {
    console.log(feature);
    console.log(feature['i']);
    var infoElement = document.getElementById('info');
    $.getJSON('http://127.0.0.1:8080/api/data?id='+feature['i'],
        function(data) {
            infoElement.innerHTML = '<h1>'+data["address"]+'</h1><p>'+data["description"]+'</p>';
            console.log(data["address"]);
        });

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
