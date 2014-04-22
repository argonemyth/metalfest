// Foundation JavaScript
$(document).foundation();

// knockou.js
$(document).ready(function () {   
    ko.applyBindings(viewModel);

    // Init date slider
    var today = new Date();
    $("#slider").dateRangeSlider({
        bounds: {
            min: new Date(today.getFullYear(), 0, 1),
            max: new Date(today.getFullYear(), 11, 31)
        },
        defaultValues: {
            min: today,
            max: new Date(today.getFullYear(), 11, 31)
        }
    // }).on("valuesChanging", function(e, data){
    }).on("valuesChanged", function(e, data){
        // console.log(data.values);
        // console.log("Something moved. min: " + data.values.min + " max: " + data.values.max);
        // viewModel.filterMarkersByDates(data.values.min, data.values.max);
        viewModel.min_date(new Date(data.values.min));
        viewModel.max_date(new Date(data.values.max));
    });
});

// This variable store any google map related objects
// like the actual map and bounds...
var google_map = {};
// an empty LatLngBounds object
google_map.fullBounds = new google.maps.LatLngBounds();

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
        map: google_map.map, // map is a global var initilized in the map binding 
        visible: false, 
        animation: google.maps.Animation.DROP
    });

    self.enableMarker = function(){
        self.marker.setVisible(true);
        // Extend the map bounds for each address
        google_map.fullBounds.extend(festLatLng);
        google_map.map.fitBounds(google_map.fullBounds);
        // self.onMap(true);
    }

    self.disableMarker = function() {
        self.marker.setVisible(false);
    }
}

function FestivalMapViewModel() {
    var self = this;
    self.festivals = ko.observableArray();
    self.min_date = ko.observable(new Date());
    self.max_date = ko.observable(new Date(self.min_date().getFullYear(), 11, 31));
    self.date_range = ko.computed(function() {
        return self.min_date() + " - " + self.max_date();
    }, self);
    // we create the subscription function manually because there is no binding
    // between date_range observable in the view.
    self.date_range.subscribe(function (date_range) {
        // console.log(date_range);
        ko.utils.arrayForEach(self.festivals(), function(item) {
            // Check if the event's start & end dates are within range
            // console.log("Festival Date: " + item.start_date());
            var festival_start_date = new Date(item.start_date());
            // console.log(festival_start_date, self.min_date(), self.max_date());
            if ( festival_start_date < self.min_date() || festival_start_date > self.max_date() ) {
                item.disableMarker();
            } else {
                item.enableMarker();
            } 
        });
    });

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

    // Filter festival markers by dates
    // self.filterMarkersByDates = function(min, max) {
    //     var min_date = Date(min);
    //     var max_date = Date(max);
    //     console.log("Going to filter markers between" + min_date + " and " + max_date);
    //     ko.utils.arrayForEach(this.festivals(), function(item) {
    //         // Check if the event's start & end dates are within range
    //         var festival_start_date = Date(item.start_date());
    //         console.log(festival_start_date, min_date, max_date);
    //         if ( festival_start_date < min_date || festival_start_date > max_date ) item.disableMarker();
    //     });
    // }

    // Related to the overlay
    self.displayOverlay = ko.observable(true);

    self.hideOverlay = function() {
        self.displayOverlay(false);
    }

    self.showOverlay = function() {
        self.displayOverlay(true);
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
            minZoom: 3,
            styles: map_style
        };
        // Be careful, map is a global now!!
        google_map.map = new google.maps.Map(element, mapOptions);
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

// Here's a custom visible bind that adds jQuery slide animation 
ko.bindingHandlers.animatedVisible = {
    init: function(element, valueAccessor) {
        // Initially set the element to be instantly visible/hidden depending on the value
        var value = valueAccessor();
        $(element).toggle(ko.unwrap(value)); // Use "unwrapObservable" so we can handle values that may or may not be observable
    },
    update: function(element, valueAccessor) {
        // Whenever the value subsequently changes, slowly fade the element in or out
        var value = valueAccessor();
        // ko.unwrap(value) ? $(element).fadeIn() : $(element).fadeOut();
        // ko.unwrap(value) ? $(element).animate({right: 0}, 600) : $(element).animate({right: "-100vw"}, 1000);
        if ( ko.unwrap(value) ) {
            $("#show-overlay-button").fadeOut();
            $(element).animate({right: 0}, 600)
        } else {
            $(element).animate({right: "-100vw"}, 600, function() {
                $("#show-overlay-button").fadeIn(200);
            });
        }
    }
};