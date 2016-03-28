//var ol = require('openlayers');


var raster = new ol.layer.Tile({
    title: "Immo Spider",
    source: new ol.source.OSM()
});

var vector = new ol.layer.Vector({
    title: 'Houses',
    source: new ol.source.Vector({
        url: 'http://127.0.0.1:8080/api/data',
        format: new ol.format.GeoJSON()
    },
    {
        tileOptions: {crossOriginKeyword: 'anonymous'},
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
            style: createPopupForAd
            //style: new ol.style.Style({
            //    image: new ol.style.Circle({
            //        radius: 5,
            //        fill: new ol.style.Fill({
            //            color: '#FF0000'
            //        }),
            //        stroke: new ol.style.Stroke({
            //            color: '#000000'
            //        })
            //    })
            //})
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

//var popup = new ol.Overlay.Popup();
//map.addOverlay(popup);


function createPopupForAd(feature) {
    //var ad = feature.get('ad');
    console.log(vector);
    var infoElement = document.getElementById('info');
    infoElement.innerHTML = 'test';
    //return new ol.Overlay.Popup(ad.get('address'));
    return new ol.style.Style({
        image: new ol.style.Circle({
            radius: 5,
            fill: new ol.style.Fill({
                color: '#FF0000'
            }),
            stroke: new ol.style.Stroke({
                color: '#000000'
            })
        })
    })
}


//// select interaction working on "pointermove"
//var selectPointerMove = new ol.interaction.Select({
//    condition: ol.events.condition.pointerMove
//});
//
//
//map.on('singleclick', function(evt) {
//    var prettyCoord = ol.coordinate.toStringHDMS(ol.proj.transform(evt.coordinate, 'EPSG:3857', 'EPSG:4326'), 2);
//    popup.show(evt.coordinate, '<div><h2>Coordinates</h2><p>' + prettyCoord + '</p></div>');
//});