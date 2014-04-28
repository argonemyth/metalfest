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

var icon_upcoming = new google.maps.MarkerImage(
    '/static/images/icons.png',
    new google.maps.Size(27, 32),
    new google.maps.Point(0,0),
    new google.maps.Point(13, 16)
)

var icon_past = new google.maps.MarkerImage(
    '/static/images/icons.png',
    new google.maps.Size(27, 32),
    new google.maps.Point(40,0),
    new google.maps.Point(13, 16)
)

var icon_nolineup = new google.maps.MarkerImage(
    '/static/images/icons.png',
    new google.maps.Size(27, 32),
    new google.maps.Point(80,0),
    new google.maps.Point(13, 16)
)

function Festival(data) {
    var self = this;

    this.title = ko.observable(data.title);
    this.url = ko.observable(data.url);
    this.start_date = ko.observable(data.start_date);
    this.end_date = ko.observable(data.end_date);
    this.lat = ko.observable(data.latitude);
    this.lng = ko.observable(data.longitude);
    this.lineup = ko.observable(ko.utils.parseJson(data.lineup)); // json string
    this.genres = ko.observable(ko.utils.parseJson(data.genres)); // json string
    this.if_past = data.if_past;

    // Google LatLng Object
    var festLatLng = new google.maps.LatLng(self.lat(),self.lng());

    // Define info window
    // http://google-maps-utility-library-v3.googlecode.com/svn/trunk/infobox/docs/reference.html
    var boxText = document.createElement("div");
    $(boxText).addClass("infobox");
    var header = '';
    if ( this.url() ) {
        header = "<h4><a target='_blank' href='" + this.url() + "'>" + this.title() + "</a></h4>"
    } else {
        header = "<h4>" + this.title() + "</h4>";
    }
    boxText.innerHTML = header +
                        "<p>" + this.start_date() + " - " + this.end_date() + "</p>"
    self.infobox = new InfoBox({
         content: boxText,
         disableAutoPan: false,
         maxWidth: 150,
         pixelOffset: new google.maps.Size(-140, 16),
         zIndex: null,
         boxStyle: {
            // background: "url('http://google-maps-utility-library-v3.googlecode.com/svn/trunk/infobox/examples/tipbox.gif') no-repeat",
            opacity: 0.85,
            width: "280px"
        },
        closeBoxMargin: "14px 8px 2px 2px",
        // closeBoxURL: "http://www.google.com/intl/en_us/mapfiles/close.gif",
        closeBoxURL: "/static/images/close.png",
        infoBoxClearance: new google.maps.Size(1, 1),
        pane: "floatPane",
        enableEventPropagation: false
    });

    // Google Map Marker Object
    var marker_icon = icon_upcoming;
    if ( this.if_past ) {
        marker_icon = icon_past;
    } else {
        if ( ! self.lineup() ) {
            marker_icon = icon_nolineup;
        }
    }

    self.marker = new google.maps.Marker({
        position: festLatLng,
        title: self.title(),
        icon: marker_icon,
        map: google_map.map, // map is a global var initilized in the map binding 
        visible: false, 
        animation: google.maps.Animation.DROP
    });

    // Event listener for clicking marker
    // google.maps.event.addListener(self.marker, 'mouseover', function() {
    google.maps.event.addListener(self.marker, 'click', function() {
        self.infobox.open(google_map.map, this);
        google_map.map.panTo(festLatLng);
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

    // Fesivals
    self.festivals = ko.observableArray();
    // Filtering options
    self.min_date = ko.observable(new Date());
    self.max_date = ko.observable(new Date(self.min_date().getFullYear(), 11, 31));
    self.date_range = ko.computed(function() {
        return self.min_date() + " - " + self.max_date();
    }, self);
    self.selected_bands = ko.observable(new Array());
    // self.bands = ["The Afternoon `Gentlemen", "Palehorse", "Metal Church", "Anaal Nathrakh", "Discharge", "Misery Index", "Gorguts", "Negură Bunget", "Blood Red Throne", "Hirax", "Bonded By Blood", "Sourvein", "Black Witchery", "In Solitude", "Graves at Sea", "Wormed", "Mystifier", "Gwydion", "Grave Miasma", "Warhammer", "Bosque", "Bölzer", "Nuclear", "For The Glory", "We Are The Damned", "Crepitation", "Nami", "Antropofagus", "Nebulous", "Executer", "Verdun", "Eryn Non Dae", "Methedras", "Revolution Within", "Eternal Storm", "In Tha Umbra", "Dolentia", "Ermo", "Age of Woe", "Trinta e Um", "Solar Corona", "Equations", "Dementia 13", "Angist", "THE QUARTET OF WOAH!", "Martelo Negro", "Serrabulho", "Vai-Te Foder", "Destroyers Of All", "Vengha", "Bed Legs", "Display of power", "Pterossauros"];
    self.bands = ko.observable(new Array());
    self.selected_genres = ko.observable(new Array());
    self.genres = ko.observable(new Array());


    // we create the subscription function manually because there is no binding
    // between date_range observable in the view.
    self.date_range.subscribe(function (date_range) {
        // console.log(date_range);
        ko.utils.arrayForEach(self.festivals(), function(item) {
            // Check if the event's start & end dates are within range
            // console.log("Festival Date: " + item.start_date());
            var festival_start_date = new Date(item.start_date());
            var festival_end_date = new Date(item.end_date());
            // console.log(festival_start_date, festival_end_date, self.min_date(), self.max_date());
            if ( (festival_start_date > self.min_date() && festival_start_date < self.max_date()) &&
                 (festival_end_date > self.min_date() && festival_end_date < self.max_date()) ) {
                item.enableMarker();
            } else {
                item.disableMarker();
            } 
        });
    });

    // filter bands
    self.selected_bands.subscribe(function (selected) {
        console.log(selected);
        ko.utils.arrayForEach(self.festivals(), function(item) {
            // We need to pickout all the festivals that have selected bands
            // a festival will be show as long as it has one band in selected
            // bands.
            if (! item.lineup() ) {
                // console.log(item.title() + " has no lineup info");
                item.disableMarker();
                return false;
            }
            var enabled = false;
            for ( var i in selected ) {
                var band = selected[i];
                if (item.lineup().indexOf(band) == -1) {
                    // console.log(band + " not found in " + item.title());
                    enabled = false;
                } else {
                    // console.log(band + " found in " + item.title());
                    enabled = true
                    break;
                }
            };

            // console.log(item.title() + ": " + enabled);
            enabled ? item.enableMarker() : item.disableMarker();
        });
    });

    // filter by genres
    self.selected_genres.subscribe(function (selected) {
        console.log(selected);
        ko.utils.arrayForEach(self.festivals(), function(item) {
            // We need to pickout all the festivals that have selected bands
            // a festival will be show as long as it has one band in selected
            // bands.
            if (! item.genres() ) {
                console.log(item.title() + " has no lineup info");
                item.disableMarker();
                return false;
            }
            var enabled = false;
            for ( var i in selected ) {
                var genre = selected[i];
                if (item.genres().indexOf(genre) == -1) {
                    // console.log(genre + " not found in " + item.title());
                    enabled = false;
                } else {
                    // console.log(genre + " found in " + item.title());
                    enabled = true
                    break;
                }
            };

            // console.log(item.title() + ": " + enabled);
            enabled ? item.enableMarker() : item.disableMarker();
        });
    });

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
        // google_map.maps.event.addDomListener(window, 'load', initialize);
    },
    update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
        var festivals = ko.utils.unwrapObservable(valueAccessor());
        // console.log("Custom binding update: "+ festivals.length);
        if (festivals.length > 0 ) {
            viewModel.showMarkers();
            var all_linup = []
            ko.utils.arrayForEach(festivals, function(item) {
                if ( item.lineup() ) all_linup = _.union(all_linup, item.lineup());
            });
            // console.log(all_linup);
            viewModel.bands(all_linup);
            var all_genres = []
            ko.utils.arrayForEach(festivals, function(item) {
                if ( item.genres() ) all_genres = _.union(all_genres, item.genres());
            });
            console.log(all_genres);
            viewModel.genres(all_genres);
        } 
    }
};

var viewModel = new FestivalMapViewModel();



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
            // $("#logo").fadeOut();
            // $("#show-overlay-button").fadeOut();
            // $(element).animate({right: 0}, 600)
            $(element).animate({top: 0}, 600)
            $("#hide-overlay-button").show();
            $("#show-overlay-button").hide();
        } else {
            // $(element).animate({right: "-100vw"}, 600, function() {
            var overlayHeight = $("#overlay").outerHeight();
            var logoHeight = $("#logo").outerHeight();
            var offset = overlayHeight-logoHeight-19;
            $(element).animate({top: "-" + offset + "px"}, 600, function() {
                // $("#logo").show();
                // $("#logo").fadeIn(200);
                // $("#logo").animate({top: 0}, 300);
                $("#hide-overlay-button").hide();
                $("#show-overlay-button").show();
            });
        }
    }
};

// select2 bind
ko.bindingHandlers.select2 = {
    init: function(element, valueAccessor, allBindingsAccessor) {
        var obj = valueAccessor(),
            allBindings = allBindingsAccessor(),
            lookupKey = allBindings.lookupKey;
        $(element).select2(obj);
        if (lookupKey) {
            var value = ko.utils.unwrapObservable(allBindings.value);
            $(element).select2('data', ko.utils.arrayFirst(obj.data.results, function(item) {
                return item[lookupKey] === value;
            }));
        }
        ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
            $(element).select2('destroy');
        });
    },
    update: function(element, valueAccessor, allBindingsAccessor) {
        return $(element).trigger('change');
    }
};

// var map_style = [{"featureType":"landscape","stylers":[{"saturation":-100},{"lightness":65},{"visibility":"on"}]},{"featureType":"poi","stylers":[{"saturation":-100},{"lightness":51},{"visibility":"simplified"}]},{"featureType":"road.highway","stylers":[{"saturation":-100},{"visibility":"simplified"}]},{"featureType":"road.arterial","stylers":[{"saturation":-100},{"lightness":30},{"visibility":"on"}]},{"featureType":"road.local","stylers":[{"saturation":-100},{"lightness":40},{"visibility":"on"}]},{"featureType":"transit","stylers":[{"saturation":-100},{"visibility":"simplified"}]},{"featureType":"administrative.province","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"labels","stylers":[{"visibility":"on"},{"lightness":-25},{"saturation":-100}]},{"featureType":"water","elementType":"geometry","stylers":[{"hue":"#ffff00"},{"lightness":-25},{"saturation":-97}]}]
var map_style = [{"featureType":"landscape","stylers":[{"saturation":-100},{"lightness":65},{"visibility":"on"}]},{"featureType":"poi","stylers":[{"saturation":-100},{"lightness":51},{"visibility":"on"}]},{"featureType":"road.highway","stylers":[{"saturation":-100},{"visibility":"simplified"}]},{"featureType":"road.arterial","stylers":[{"saturation":-100},{"lightness":30},{"visibility":"on"}]},{"featureType":"road.local","stylers":[{"saturation":-100},{"lightness":40},{"visibility":"on"}]},{"featureType":"transit","stylers":[{"saturation":-100},{"visibility":"simplified"}]},{"featureType":"administrative.province","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"labels","stylers":[{"visibility":"on"},{"lightness":-25},{"saturation":-100}]},{"featureType":"water","elementType":"geometry","stylers":[{"hue":"#00DFFC"},{"lightness":-50},{"saturation":-20}]}]
// var map_style = [{"featureType":"water","elementType":"all","stylers":[{"hue":"#e9ebed"},{"saturation":-78},{"lightness":67},{"visibility":"simplified"}]},{"featureType":"landscape","elementType":"all","stylers":[{"hue":"#ffffff"},{"saturation":-100},{"lightness":100},{"visibility":"simplified"}]},{"featureType":"road","elementType":"geometry","stylers":[{"hue":"#bbc0c4"},{"saturation":-93},{"lightness":31},{"visibility":"simplified"}]},{"featureType":"poi","elementType":"all","stylers":[{"hue":"#ffffff"},{"saturation":-100},{"lightness":100},{"visibility":"off"}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"hue":"#e9ebed"},{"saturation":-90},{"lightness":-8},{"visibility":"simplified"}]},{"featureType":"transit","elementType":"all","stylers":[{"hue":"#e9ebed"},{"saturation":10},{"lightness":69},{"visibility":"on"}]},{"featureType":"administrative.locality","elementType":"all","stylers":[{"hue":"#2c2e33"},{"saturation":7},{"lightness":19},{"visibility":"on"}]},{"featureType":"road","elementType":"labels","stylers":[{"hue":"#bbc0c4"},{"saturation":-93},{"lightness":31},{"visibility":"on"}]},{"featureType":"road.arterial","elementType":"labels","stylers":[{"hue":"#bbc0c4"},{"saturation":-93},{"lightness":-2},{"visibility":"simplified"}]}]
// Neurtral-blue: http://snazzymaps.com/style/13/neutral-blue
// var map_style = [{"featureType":"water","elementType":"geometry","stylers":[{"color":"#193341"}]},{"featureType":"landscape","elementType":"geometry","stylers":[{"color":"#2c5a71"}]},{"featureType":"road","elementType":"geometry","stylers":[{"color":"#29768a"},{"lightness":-37}]},{"featureType":"poi","elementType":"geometry","stylers":[{"color":"#406d80"}]},{"featureType":"transit","elementType":"geometry","stylers":[{"color":"#406d80"}]},{"elementType":"labels.text.stroke","stylers":[{"visibility":"on"},{"color":"#3e606f"},{"weight":2},{"gamma":0.84}]},{"elementType":"labels.text.fill","stylers":[{"color":"#ffffff"}]},{"featureType":"administrative","elementType":"geometry","stylers":[{"weight":0.6},{"color":"#1a3541"}]},{"elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"poi.park","elementType":"geometry","stylers":[{"color":"#2c5a71"}]}]
// Styled based on: Bentley: http://snazzymaps.com/style/43/bentley
 