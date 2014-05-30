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
            // min: today,
            min: new Date(today.getFullYear(), 0, 1),
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

    // Custom humane notifier
    humane.info = humane.spawn({ addnCls: 'info', timeout: 3000, clickToClose: true})
    humane.error = humane.spawn({ addnCls: 'error', timeout: 3000, clickToClose: true })
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

    // I know those data dosn't need to be observables.
    this.title = ko.observable(data.title);
    this.url = ko.observable(data.url);
    // this.start_date = ko.observable(data.start_date);
    // this.end_date = ko.observable(data.end_date);
    this.start_date = new Date(data.start_date);
    this.end_date = new Date(data.end_date);
    this.lat = ko.observable(data.latitude);
    this.lng = ko.observable(data.longitude);
    this.lineup = ko.observable(ko.utils.parseJson(data.lineup)); // json string
    this.genres = ko.observable(ko.utils.parseJson(data.genres)); // json string
    this.if_past = data.if_past;
    this.detail_url = data.detail_url; // url of festival detail
    this.slug = data.slug;

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
    // var dates = '';
    // if ( this.start_date && this.end_date ) {
    //     dates = "<p>" + this.start_date.toDateString() + " - " + this.end_date.toDateString() + "</p>"
    // }
    var loader = '<hr><div class="festival-loader '+ this.slug +'"><i class="fa fa-refresh fa-spin fa-2x"></i><p>Loading more info...</p></div>';
    // boxText.innerHTML = header + dates + loader;
    boxText.innerHTML = header + loader;
    self.infobox = new InfoBox({
         content: boxText,
         disableAutoPan: false,
         // maxWidth: 150,
         // maxWidth: 290,
         pixelOffset: new google.maps.Size(-140, 16),
         zIndex: null,
         boxStyle: {
            // background: "url('http://google-maps-utility-library-v3.googlecode.com/svn/trunk/infobox/examples/tipbox.gif') no-repeat",
            opacity: 0.85,
            width: "296px"
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
        // $(".festival-loader." + this.slug).load(this.festival_url);
        // self.infobox.setContent(boxText);
        $.ajax({
            url: self.detail_url,
        }).done(function(html) {
            boxText.innerHTML = html;
            // console.log("set custom scrollbar");
            // console.log($(boxText).find(".artists li"));
            // $(boxText).find(".artists").mCustomScrollbar();
            /*
            $(boxText).find(".artists").mCustomScrollbar({
                advanced:{
                    updateOnContentResize: true
                }
            });
            */
            // $.when( self.infobox.setContent(boxText) ).done(function() {
            //     console.log("Infobox finished");
            //     $(boxText).find(".artists").jScrollPane();
            // })
            // BUG: The first click won't work, and then works on every infobox...
            self.infobox.setContent(boxText);
            setTimeout(function() {
                // A hack to make sure infobox loadeded the content
                var artist_list = $(boxText).find(".artists");
                if ( $(artist_list).length ) $(artist_list).jScrollPane();
                // bind 
                ko.applyBindings(viewModel, boxText);
                // Need to get abide working for dynamically loaded form.
                // Not sure if the callidng foundation() is the correct way to go
                // but Abide works now.
                // $(document).foundation(); 
            }, 300);
        });
        google_map.map.panTo(festLatLng);
    });

    // we need remove the boxText ko binding when the infobox closes
    google.maps.event.addListener(self.infobox, 'closeclick', function() {
        ko.cleanNode(boxText);
    });

    self.enableMarker = function(){
        self.marker.setVisible(true);
        // Extend the map bounds for each address
        google_map.fullBounds.extend(festLatLng);
        // google_map.map.fitBounds(google_map.fullBounds);
        // self.onMap(true);
    }

    self.disableMarker = function() {
        self.marker.setVisible(false);
    }
}

function Event(data) {
    var self = this;

    // I know those data dosn't need to be observables.
    this.name = data.name;
    // this.url = data.url;
    // this.date = ko.observable(data.date);
    this.date = new Date(data.date);
    this.lat = data.latitude;
    this.lng = data.longitude;
    // this.lineup = ko.utils.parseJson(data.lineup); // json string
    // this.detail_url = data.detail_url; // url of festival detail
    this.slug = "temp";

    // Google LatLng Object
    var festLatLng = new google.maps.LatLng(self.lat,self.lng);

    // Define info window
    var boxText = document.createElement("div");
    $(boxText).addClass("infobox");
    var header = "<h4>" + this.name + "</h4>";

    if ( this.date ) {
        dates = "<p>" + this.date.toDateString() + "</p>"
    }

    var loader = '<hr><div class="festival-loader '+ this.slug +'"><i class="fa fa-refresh fa-spin fa-2x"></i><p>Loading more info...</p></div>';
    // boxText.innerHTML = header + dates + loader;
    boxText.innerHTML = header + loader;
    self.infobox = new InfoBox({
         content: boxText,
         disableAutoPan: false,
         pixelOffset: new google.maps.Size(-140, 16),
         zIndex: null,
         boxStyle: {
            opacity: 0.85,
            width: "296px"
        },
        closeBoxMargin: "14px 8px 2px 2px",
        closeBoxURL: "/static/images/close.png",
        infoBoxClearance: new google.maps.Size(1, 1),
        pane: "floatPane",
        enableEventPropagation: false
    });

    // Google Map Marker Object
    self.marker = new google.maps.Marker({
        position: festLatLng,
        title: self.name,
        icon: icon_upcoming,
        map: google_map.map, // map is a global var initilized in the map binding 
        visible: false, 
        animation: google.maps.Animation.DROP
    });

    // Event listener for clicking marker
    google.maps.event.addListener(self.marker, 'click', function() {
        self.infobox.open(google_map.map, this);
        $.ajax({
            url: self.detail_url,
        }).done(function(html) {
            boxText.innerHTML = html;
            self.infobox.setContent(boxText);
            setTimeout(function() {
                // A hack to make sure infobox loadeded the content
                var artist_list = $(boxText).find(".artists");
                if ( $(artist_list).length ) $(artist_list).jScrollPane();
                ko.applyBindings(viewModel, boxText);
            }, 300);
        });
        google_map.map.panTo(festLatLng);
    });

    // we need remove the boxText ko binding when the infobox closes
    google.maps.event.addListener(self.infobox, 'closeclick', function() {
        ko.cleanNode(boxText);
    });

    self.enableMarker = function(){
        self.marker.setVisible(true);
        google_map.fullBounds.extend(festLatLng);
    }

    self.disableMarker = function() {
        self.marker.setVisible(false);
    }
}

function FestivalMapViewModel() {
    var self = this;

    // Fesivals && events
    self.festivals = ko.observableArray();
    self.events = ko.observableArray(); //inside of the array, it's a object

    // Filtering options
    // self.min_date = ko.observable(new Date());
    var today = new Date();
    self.min_date = ko.observable(new Date(today.getFullYear(), 0, 31));
    self.max_date = ko.observable(new Date(today.getFullYear(), 11, 31));
    self.date_range = ko.computed(function() {
        return self.min_date() + " - " + self.max_date();
    }, self);
    self.selected_bands_str = ko.observable();
    self.selected_bands = ko.observable(new Array());
    self.selected_bands2 = ko.observableArray();
    // self.bands = ["The Afternoon `Gentlemen", "Palehorse", "Metal Church", "Anaal Nathrakh", "Discharge", "Misery Index", "Gorguts", "Negură Bunget", "Blood Red Throne", "Hirax", "Bonded By Blood", "Sourvein", "Black Witchery", "In Solitude", "Graves at Sea", "Wormed", "Mystifier", "Gwydion", "Grave Miasma", "Warhammer", "Bosque", "Bölzer", "Nuclear", "For The Glory", "We Are The Damned", "Crepitation", "Nami", "Antropofagus", "Nebulous", "Executer", "Verdun", "Eryn Non Dae", "Methedras", "Revolution Within", "Eternal Storm", "In Tha Umbra", "Dolentia", "Ermo", "Age of Woe", "Trinta e Um", "Solar Corona", "Equations", "Dementia 13", "Angist", "THE QUARTET OF WOAH!", "Martelo Negro", "Serrabulho", "Vai-Te Foder", "Destroyers Of All", "Vengha", "Bed Legs", "Display of power", "Pterossauros"];
    self.bands = ko.observable(new Array());
    self.selected_genres_str = ko.observable();
    self.selected_genres = ko.observable(new Array());
    self.genres = ko.observable(new Array());

    self.displayedFestivals = ko.computed(function() {
        // Represents a filtered list of festivals
        return ko.utils.arrayFilter(self.festivals(), function(festival) {
            var display_by_dates = false;
            var display_by_bands = false;
            var display_by_genres = false;

            // Filter by dates
            if ( (festival.start_date > self.min_date() && festival.start_date < self.max_date()) &&
                 (festival.end_date > self.min_date() && festival.end_date < self.max_date()) ) {
                display_by_dates = true;
            }

            // Filter by bands
            if ( self.selected_bands().length == 0 ) {
                display_by_bands = true;
            } else {
                if ( ! festival.lineup() ) {
                    display_by_bands = false;
                } else {
                    // we have lineup info & user selected some bands
                    var found = false;
                    for ( var i in self.selected_bands() ) {
                        var band = self.selected_bands()[i];
                        if (festival.lineup().indexOf(band) == -1) {
                            // console.log(band + " not found in " + festival.title());
                            found = false;
                        } else {
                            // console.log(band + " found in " + festival.title());
                            found = true
                            break;
                        }
                    };
                    if ( found ) display_by_bands = true;
                }
            }

            // Filter by Genres
            if ( self.selected_genres().length == 0 ) {
                display_by_genres = true;
            } else {
                if ( ! festival.genres() ) {
                    display_by_genres = false;
                } else {
                    // we have genre info & user selected some genres
                    var found = false;
                    for ( var i in self.selected_genres() ) {
                        var genre = self.selected_genres()[i];
                        if (festival.genres().indexOf(genre) == -1) {
                            // console.log(genre + " not found in " + festival.title());
                            found = false;
                        } else {
                            // console.log(genre + " found in " + festival.title());
                            found = true
                            break;
                        }
                    };
                    if ( found ) display_by_genres = true;
                }
            }

            // If all three filter function return ture, the marker will show
            /*
            if ( display_by_dates && display_by_genres && display_by_bands ) {
                console.log("Should show");
                return true;
            } else {
                console.log("Date filter (" + festival.start_date + "-" + festival.end_date + "): " + display_by_dates);
                console.log("Band filter: " + display_by_bands);
                console.log("Genre filter: " + display_by_genres);
            }
            */
            return display_by_dates && display_by_genres && display_by_bands
        })

    }, this);
    
    self.selected_bands_str.subscribe(function(bands) {
        // Need to turn strings to the array
        if (bands) {
            var band_array = bands.split(',');
            self.selected_bands(band_array);
            $.each(band_array, function(index, band) {
                if ( self.selected_bands2.indexOf(band) === -1) {
                    self.selected_bands2.push(band);
                }
            });
            $.each(self.selected_bands2(), function(index, band) {
                if ( band_array.indexOf(band) === -1) {
                    self.selected_bands2.remove(band);
                }
            });
        } else {
            // reset bands 
            self.selected_bands([]);
            self.selected_bands2.removeAll();
        }
    });

    self.selected_bands2.subscribe(function(changes){
        var band = changes[0].value;
        // console.log(changes[0]);
        if (changes[0].status === "added") {
            console.log(band + " is added");
            var data = {"artist": band};
            $.get("/festivals/events/", data, function(returnedData) {
                if (returnedData.length > 0 ) {
                    var mappedEvents = $.map(returnedData, function(item) { return new Event(item) });
                    self.events.push({"band": band, "events": mappedEvents}) 
                } else {
                    console.log("No event found!");
                }
            })
        } else {
            console.log(band + " is removed");
            self.events.remove(function(item) { return item.band == band });
        }
    }, null, "arrayChange");


    // self.selected_bands.subscribe(function (selected) {
    //     if ( selected ) {
    //         // console.log("Seleted Bands: " + selected);
    //         // 1. Check if selected are in events array
    //         $.each(selected, function(index, band){
    //             obj = _.find(self.events(), function(obj) { return obj.band == band })
    //             if ( obj == undefined ) {
    //                 console.log("Adding bands to events");
    //                 self.events.push({'band': band});
    //             } else {
    //                 console.log(obj + "is already in the event list");
    //             }
    //         });
    //     } else {
    //         console.log("Nothing selected, reset events array");
    //     }
    // });

    self.selected_genres_str.subscribe(function(genres) {
        // Need to turn strings to the array
        if (genres) {
            self.selected_genres(genres.split(','));
            // console.log(self.selected_genres());
        } else {
            // reset genres
            self.selected_genres([]);
        }
    });

    self.events.subscribe(function(changes) {
         var changed_object = changes[0].value;
        if (changes[0].status === "added") {
            // console.log("Going to enable all markers");
            ko.utils.arrayForEach(changed_object.events, function(item) {
                item.enableMarker();
            });
        } else {
            ko.utils.arrayForEach(changed_object.events, function(item) {
                item.disableMarker();
            });
        }
    }, null, "arrayChange");

    self.displayedFestivals.subscribe(function (festivals) {
        // console.log("displayedFestival changed.");
        ko.utils.arrayForEach(self.festivals(), function(item) {
            // Only display the one that are in displayedFestival
            if ( festivals.indexOf(item) == -1 ) {
                item.disableMarker();
            } else {
                item.enableMarker()
            }
        });
        // Google map auto zoom
        // google_map.map.panToBounds(google_map.fullBounds);
        // google_map.map.fitBounds(google_map.fullBounds);
    });

    /*
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
    */

    // Load initial festivals from server, convert it to Task instances, then populate self.festivals
    $.getJSON("/festivals/all/", function(data) {
        var festival_list = data['festivals']
        var mappedFestivals = $.map(festival_list, function(item) { return new Festival(item) });
        self.festivals(mappedFestivals);
        $("#loader").hide();
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

    // Get a list of all the band names

    // $.getJSON("/festivals/artists/?search=ar", function(data) {
    //     // console.log(data);
    //     var artist_list = data;
    //     var all_artists = [];
    //     ko.utils.arrayForEach(artist_list, function(item) {
    //         // console.log(item.name);
    //         all_artists.push(item.name);
    //     });
    //     self.bands(all_artists);
    // });

    self.bandQuery = function (query) {
        // build response for echoed ajax test
        // console.log(query);
        // var bands = [];
        // ko.utils.arrayForEach(self.bands, function (band) {
        //     if (band.text.search(new RegExp(query.term, 'i')) >= 0) {
        //         bands.push(band);
        //     }
        // });
        // console.log(bands);
        $.ajax({
            url: '/festivals/artists/',
            type: 'GET',
            dataType: 'json',
            data: {
                // search: JSON.stringify(states)
                search: query.term
            },
            success: function (data) {
                var bands = [];
                for ( i in data ) {
                    bands.push({id: data[i].name, text: data[i].name});
                }
                query.callback({
                    results: bands 
                });
            }
        });
    };

    self.genreQuery = function (query) {
        $.ajax({
            url: '/festivals/genres/',
            type: 'GET',
            dataType: 'json',
            data: {
                // search: JSON.stringify(states)
                search: query.term
            },
            success: function (data) {
                var genres = [];
                for ( i in data ) {
                    genres.push({id: data[i].name, text: data[i].name});
                }
                query.callback({
                    results: genres
                });
            }
        });
    };

    self.showReportForm = function(vm, event) {
        var parentSection = $(event.target).parents("section");
        var formSection = parentSection.next();
        parentSection.hide();
        formSection.show();
        $(formSection).children('form').validate({
            errorElement: "small",
            rules: {
                info_type: {
                    required: true,
                    minlength: 1
                }
            },
            errorPlacement: function(error, element) {
                if (element.attr("name") == "info_type" )
                    error.appendTo("#div_id_info_type");
                else
                    error.insertAfter(element);
            } 
        });
    } 

    self.submitReportForm = function (form) {
        var $form = $(form);
       //actually save stuff, call ajax, submit form, etc;
        // console.log($form.attr("action"));
        // console.log($form.serialize());

        if ( $form.valid() ) {
            // console.log("Form is valie, going to submit");
            var posting = $.post( $form.attr("action"), $form.serialize() );

            posting.done(function( data ) {
                if (data.status === "success") {
                    humane.info(data.message);
                    $form.parents("section").hide();
                    $form.parents("section").prev().show();
                } else {
                    $form.html(data);
                }
            });
        }
    }
}

// This binding only control the initalization of the google map with all the festivals.
ko.bindingHandlers.map = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
        var festivals = ko.utils.unwrapObservable(valueAccessor());
        // console.log("Custom binding init: " + festivals.length);
        // var latLng = new google.maps.LatLng(55, 11);
        // var latLng = new google.maps.LatLng(40, 3);
        var latLng = new google.maps.LatLng(30, 25);
        var mapOptions = {
            center: latLng,
            zoom: 2, 
            // zoom: 5, 
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
        if (festivals.length > 0 ) {
            viewModel.showMarkers();
            // var all_linup = []
            // ko.utils.arrayForEach(festivals, function(item) {
            //     if ( item.lineup() ) all_linup = _.union(all_linup, item.lineup());
            // });
            // console.log(all_linup);
            // viewModel.bands(all_linup);
            var all_genres = []
            ko.utils.arrayForEach(festivals, function(item) {
                if ( item.genres() ) all_genres = _.union(all_genres, item.genres());
            });
            // console.log(all_genres);
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
        var clientWidth = $(document).width();
        // ko.unwrap(value) ? $(element).fadeIn() : $(element).fadeOut();
        // ko.unwrap(value) ? $(element).animate({right: 0}, 600) : $(element).animate({right: "-100vw"}, 1000);
        if ( ko.unwrap(value) ) {
            // $("#logo").fadeOut();
            // $("#show-overlay-button").fadeOut();
            // $(element).animate({right: 0}, 600)
            if ( clientWidth <= 640 ) {
                $("#overlay").css("overflow-y", "scroll");
                $(".hide-for-small-slideup").show();
            }
            $(element).animate({top: 0}, 600)
            $("#hide-overlay-button").show();
            $("#show-overlay-button").hide();
        } else {
            // $(element).animate({right: "-100vw"}, 600, function() {
            // var overlayHeight = $("#overlay").outerHeight();
            if ( clientWidth > 640 ) {
                var overlayHeight = $("#overlay").outerHeight();
                var logoHeight = $("#logo").outerHeight();
                var offset = overlayHeight-logoHeight-19;
            } else {
                // Reducing info on mobile phone
                $(".hide-for-small-slideup").hide();
                var overlayHeight = $("#overlay").outerHeight();
                var logoHeight = $("#logo").outerHeight();
                var offset = overlayHeight-logoHeight;
            }
            $(element).animate({top: "-" + offset + "px"}, 600, function() {
                // $("#logo").show();
                // $("#logo").fadeIn(200);
                // $("#logo").animate({top: 0}, 300);
                $("#hide-overlay-button").hide();
                $("#show-overlay-button").show();
                $("#overlay").css("overflow", "hidden");
            });
        }
    }
};

// select2 bind
ko.bindingHandlers.select2 = {
    init: function(element, valueAccessor, allBindingsAccessor) {
        var obj = valueAccessor(), // this is the select2 options
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
// var map_style = [{"featureType":"water","elementType":"all","stylers":[{"hue":"#e9ebed"},{"saturation":-78},{"lightness":67},{"visibility":"simplified"}]},{"featureType":"landscape","elementType":"all","stylers":[{"hue":"#ffffff"},{"saturation":-100},{"lightness":100},{"visibility":"simplified"}]},{"featureType":"road","elementType":"geometry","stylers":[{"hue":"#bbc0c4"},{"saturation":-93},{"lightness":31},{"visibility":"simplified"}]},{"featureType":"poi","elementType":"all","stylers":[{"hue":"#ffffff"},{"saturation":-100},{"lightness":100},{"visibility":"off"}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"hue":"#e9ebed"},{"saturation":-90},{"lightness":-8},{"visibility":"simplified"}]},{"featureType":"transit","elementType":"all","stylers":[{"hue":"#e9ebed"},{"saturation":10},{"lightness":69},{"visibility":"on"}]},{"featureType":"administrative.locality","elementType":"all","stylers":[{"hue":"#2c2e33"},{"saturation":7},{"lightness":19},{"visibility":"on"}]},{"featureType":"road","elementType":"labels","stylers":[{"hue":"#bbc0c4"},{"saturation":-93},{"lightness":31},{"visibility":"on"}]},{"featureType":"road.arterial","elementType":"labels","stylers":[{"hue":"#bbc0c4"},{"saturation":-93},{"lightness":-2},{"visibility":"simplified"}]}]
// Neurtral-blue: http://snazzymaps.com/style/13/neutral-blue
// var map_style = [{"featureType":"water","elementType":"geometry","stylers":[{"color":"#193341"}]},{"featureType":"landscape","elementType":"geometry","stylers":[{"color":"#2c5a71"}]},{"featureType":"road","elementType":"geometry","stylers":[{"color":"#29768a"},{"lightness":-37}]},{"featureType":"poi","elementType":"geometry","stylers":[{"color":"#406d80"}]},{"featureType":"transit","elementType":"geometry","stylers":[{"color":"#406d80"}]},{"elementType":"labels.text.stroke","stylers":[{"visibility":"on"},{"color":"#3e606f"},{"weight":2},{"gamma":0.84}]},{"elementType":"labels.text.fill","stylers":[{"color":"#ffffff"}]},{"featureType":"administrative","elementType":"geometry","stylers":[{"weight":0.6},{"color":"#1a3541"}]},{"elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"poi.park","elementType":"geometry","stylers":[{"color":"#2c5a71"}]}]
// Styled based on: Bentley: http://snazzymaps.com/style/43/bentley
// var map_style = [{"featureType":"landscape","stylers":[{"saturation":-100},{"lightness":65},{"visibility":"on"}]},{"featureType":"poi","stylers":[{"saturation":-100},{"lightness":51},{"visibility":"on"}]},{"featureType":"road.highway","stylers":[{"saturation":-100},{"visibility":"simplified"}]},{"featureType":"road.arterial","stylers":[{"saturation":-100},{"lightness":30},{"visibility":"on"}]},{"featureType":"road.local","stylers":[{"saturation":-100},{"lightness":40},{"visibility":"on"}]},{"featureType":"transit","stylers":[{"saturation":-100},{"visibility":"simplified"}]},{"featureType":"administrative.province","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"labels","stylers":[{"visibility":"on"},{"lightness":-25},{"saturation":-100}]},{"featureType":"water","elementType":"geometry","stylers":[{"hue":"#00DFFC"},{"lightness":-60},{"saturation":-20}]}]
var map_style = [
    {
        "stylers": [
            {
                "color": "#131314"
            }
        ]
    },
    // {"featureType":"landscape","stylers":[{"saturation":-100},{"lightness":65},{"visibility":"on"}]},
    {"featureType":"poi","stylers":[{"color": "#000000"},{"visibility":"on"}]},
    // {"featureType":"road.highway","stylers":[{"saturation":-100},{"visibility":"simplified"}]},
    // {"featureType":"road.highway","stylers":[{"visibility":"simplified"}]},
    // {"featureType":"road.arterial","stylers":[{"saturation":-100},{"lightness":30},{"visibility":"on"}]},
    // {"featureType":"road.local","stylers":[{"saturation":-100},{"lightness":40},{"visibility":"on"}]},
    {"featureType":"road.local","stylers":[{"color": "#000000"},{"visibility":"on"}]},
    // {"featureType":"transit","stylers":[{"saturation":-100},{"visibility":"simplified"}]},
    {"featureType":"transit","stylers":[{"visibility":"simplified"}]},
    {"featureType":"administrative.province","stylers":[{"visibility":"off"}]},
    // {"featureType":"water","elementType":"labels","stylers":[{"visibility":"on"},{"saturation":-100},{"lightness":-25}]},
    // {"featureType":"water","elementType":"geometry","stylers":[{"color":"#212121"}]}
    {
        "featureType": "water",
        "stylers": [
            {
                "color": "#131313"
            },
            {
                "lightness": 7
            }
        ]
    },
    {
        "elementType": "labels.text.fill",
        "stylers": [
            {
                "visibility": "on"
            },
            {
                "lightness": 25
            }
        ]
    }/*,
    {
        "elementType": "labels.icon",
        "stylers": [
            {
                "visibility": "on"
            },
            {
                "inverse_lightness": true
            }
        ]
    }*/
];