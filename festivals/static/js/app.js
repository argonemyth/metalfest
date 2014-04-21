// Foundation JavaScript
$(document).foundation();

// knockou.js
$(document).ready(function () {   
    ko.applyBindings(viewModel);

});

function Festival(data) {
    var self = this;

    this.title = ko.observable(data.title);
    this.start_date = ko.observable(data.start_date);
    this.end_date = ko.observable(data.end_date);
    this.lat = ko.observable(data.latitude);
    this.lng = ko.observable(data.longitude);

    // Google LatLng Object
    var festLatLng = new google.maps.LatLng(self.lat(),self.lng());

    // Google Map Marker Object
    self.marker = new google.maps.Marker({
        position: festLatLng,
        title: self.title(),
        // icon: 'custome_icon.png',
        map: map, // map is a global var initilized in the map binding 
        visible: false, 
        animation: google.maps.Animation.DROP
    });

    self.enableMarker = function(){
        self.marker.setVisible(true);
        // Extend the map bounds for each address
        // fullBounds.extend(currLatLng);
        // map.fitBounds(cm.koThree.fullBounds);
        // self.onMap(true);
    }
}

function FestivalMapViewModel() {
    var self = this;
    self.festivals = ko.observableArray();

    self.myMap = ko.observable({
        lat: ko.observable(55),
        lng: ko.observable(11)});

    // Load initial festivals from server, convert it to Task instances, then populate self.festivals
    $.getJSON("/festivals/all/", function(data) {
        var festival_list = data['festivals']
        var mappedFestivals = $.map(festival_list, function(item) { return new Festival(item) });
        self.festivals(mappedFestivals);
    });

    // Show all festival markers
    self.showMarkers = function() {
        // console.log("Going to enable all markers");
        ko.utils.arrayForEach(this.festivals(), function(item) {
            item.enableMarker();
        });
    }
}

ko.bindingHandlers.map = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
        var festivals = ko.utils.unwrapObservable(valueAccessor());
        // console.log("Custom binding init: " + festivals.length);
        var latLng = new google.maps.LatLng(55, 11);
        var mapOptions = {
            center: latLng,
            zoom: 5, 
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            mapTypeControl: false,
            styles: map_style
        };
        // Be careful, map is a global now!!
        map = new google.maps.Map(element, mapOptions);
    },
    update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
        var festivals = ko.utils.unwrapObservable(valueAccessor());
        // console.log("Custom binding update: "+ festivals.length);
        if (festivals.length > 0 ) viewModel.showMarkers();
    }
};

var viewModel = new FestivalMapViewModel();

// var map_style = [{"featureType":"landscape","stylers":[{"saturation":-100},{"lightness":65},{"visibility":"on"}]},{"featureType":"poi","stylers":[{"saturation":-100},{"lightness":51},{"visibility":"simplified"}]},{"featureType":"road.highway","stylers":[{"saturation":-100},{"visibility":"simplified"}]},{"featureType":"road.arterial","stylers":[{"saturation":-100},{"lightness":30},{"visibility":"on"}]},{"featureType":"road.local","stylers":[{"saturation":-100},{"lightness":40},{"visibility":"on"}]},{"featureType":"transit","stylers":[{"saturation":-100},{"visibility":"simplified"}]},{"featureType":"administrative.province","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"labels","stylers":[{"visibility":"on"},{"lightness":-25},{"saturation":-100}]},{"featureType":"water","elementType":"geometry","stylers":[{"hue":"#ffff00"},{"lightness":-25},{"saturation":-97}]}]
var map_style = [{"featureType":"water","elementType":"all","stylers":[{"hue":"#e9ebed"},{"saturation":-78},{"lightness":67},{"visibility":"simplified"}]},{"featureType":"landscape","elementType":"all","stylers":[{"hue":"#ffffff"},{"saturation":-100},{"lightness":100},{"visibility":"simplified"}]},{"featureType":"road","elementType":"geometry","stylers":[{"hue":"#bbc0c4"},{"saturation":-93},{"lightness":31},{"visibility":"simplified"}]},{"featureType":"poi","elementType":"all","stylers":[{"hue":"#ffffff"},{"saturation":-100},{"lightness":100},{"visibility":"off"}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"hue":"#e9ebed"},{"saturation":-90},{"lightness":-8},{"visibility":"simplified"}]},{"featureType":"transit","elementType":"all","stylers":[{"hue":"#e9ebed"},{"saturation":10},{"lightness":69},{"visibility":"on"}]},{"featureType":"administrative.locality","elementType":"all","stylers":[{"hue":"#2c2e33"},{"saturation":7},{"lightness":19},{"visibility":"on"}]},{"featureType":"road","elementType":"labels","stylers":[{"hue":"#bbc0c4"},{"saturation":-93},{"lightness":31},{"visibility":"on"}]},{"featureType":"road.arterial","elementType":"labels","stylers":[{"hue":"#bbc0c4"},{"saturation":-93},{"lightness":-2},{"visibility":"simplified"}]}]