define(['jquery', 'knockout', 'underscore', 'humane', 'text!./map.html', 'foundation', 'slider', 'select2', 'validation', 'jscrollpane'], function($, ko, _, humane, mapTemplate) {
    function defaultDateRange() {
        var minDate = new Date();
        var maxDate = new Date();
        minDate.setMonth(minDate.getMonth() - 2); 
        maxDate.setMonth(maxDate.getMonth() + 10);
        return {'minDate': minDate, 'maxDate': maxDate,
                'minDateStr': minDate.toDateString(),
                'maxDateStr': maxDate.toDateString()};
    }

    var date_range = defaultDateRange();

    $(document).ready(function () {   
        // Init date slider
        // var today = new Date();
        // $("#slider").dateRangeSlider({
        //     bounds: {
        //         // min: new Date(today.getFullYear(), 0, 1),
        //         // max: new Date(today.getFullYear(), 11, 31)
        //         min: date_range.minDate,
        //         max: date_range.maxDate
        //     },
        //     defaultValues: {
        //         // min: new Date(today.getFullYear(), 0, 1),
        //         // max: new Date(today.getFullYear(), 11, 31)
        //         min: date_range.minDate,
        //         max: date_range.maxDate
        //     }
        // }).on("valuesChanged", function(e, data){
        //     // viewModel.filterMarkersByDates(data.values.min, data.values.max);
        //     // viewModel.min_date(new Date(data.values.min));
        //     // viewModel.max_date(new Date(data.values.max));
        //     FestivalMapViewModel.min_date(new Date(data.values.min));
        //     FestivalMapViewModel.max_date(new Date(data.values.max));
        // });

    // Custom humane notifier
    humane.info = humane.spawn({ addnCls: 'info', timeout: 3000, clickToClose: true})
    humane.error = humane.spawn({ addnCls: 'error', timeout: 3000, clickToClose: true })
    });


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

    var icon_gig = new google.maps.MarkerImage(
        '/static/images/icons.png',
        new google.maps.Size(27, 32),
        new google.maps.Point(120,0),
        new google.maps.Point(13, 16)
    )

    function Festival(data) {
        var self = this;

        // I know those data dosn't need to be observables.
        // this.title = ko.observable(data.title);
        // this.url = ko.observable(data.url);
        this.title = data.title;
        this.title_long = data.title_long;
        this.url = data.url;
        // this.start_date = ko.observable(data.start_date);
        // this.end_date = ko.observable(data.end_date);
        this.start_date = new Date(data.start_date);
        this.end_date = new Date(data.end_date);
        this.lat = data.latitude;
        this.lng = data.longitude;
        this.country = data.country;
        // this.lineup = ko.observable(ko.utils.parseJson(data.lineup)); // json string
        // this.genres = ko.observable(ko.utils.parseJson(data.genres)); // json string
        this.lineup = ko.utils.parseJson(data.lineup); // json string
        this.genres = ko.utils.parseJson(data.genres); // json string
        this.if_past = data.if_past;
        this.detail_url = data.detail_url; // url of festival detail
        this.slug = data.slug;

        // Google LatLng Object
        var festLatLng = new google.maps.LatLng(self.lat,self.lng);

        // Define info window
        // http://google-maps-utility-library-v3.googlecode.com/svn/trunk/infobox/docs/reference.html
        var boxText = document.createElement("div");
        $(boxText).addClass("infobox");
        var header = '';
        if ( this.url ) {
            header = "<h4><a target='_blank' href='" + this.url + "'>" + this.title + "</a></h4>"
        } else {
            header = "<h4>" + this.title + "</h4>";
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
            if ( ! self.lineup ) {
                marker_icon = icon_nolineup;
            }
        }

        self.marker = new google.maps.Marker({
            position: festLatLng,
            title: self.title_long,
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
            self.infobox.close();
            ko.cleanNode(boxText);
        }
    }

    function Gig(data) {
        var self = this;

        this.name = data.title;
        // this.url = data.url;
        this.date = new Date(data.start_date);
        this.lat = data.latitude;
        this.lng = data.longitude;
        this.location = data.location;
        this.country = data.country;
        this.lineup = data.artists;

        // Google LatLng Object
        var festLatLng = new google.maps.LatLng(self.lat,self.lng);

        // Define info window
        // TODO: Don't like it!
        var boxText = document.createElement("div");
        $(boxText).addClass("infobox");
        var header = "<h4>" + this.name + "</h4>";
        var dates = "<div class='date'>" + this.date.toDateString() + "</div>";
        var location = '<div class="location">' + data.location + ', ' + data.country + '</div>'

        var lineup_html = "";
        if ( this.lineup.length > 0 ) {
            lineup_html += '<ul class="artists inline-list">';
            for (var i = 0; i < this.lineup.length; i++) { 
                var artist = this.lineup[i];
                var line = '<li>';
                if ( artist.avatar_url_small ) {
                    if ( artist.url ) {
                        line += '<a href="' + artist.url +'" target="_blank"><img src="' + artist.avatar_url_small + '" alt="' + artist.name +'" title="' + artist.name +'"></a>';
                    } else {
                        line += '<img src="' + artist.avatar_url_small + '" alt="' + artist.name +'" title="' + artist.name +'">';
                    }
                } else {
                    if ( artist.url ) {
                        line += '<a href="' + artist.url +'" target="_blank"><img src="http://placehold.it/65x65&text=' + artist.name + '" alt="' + artist.name +'" title="' + artist.name +'"></a>';
                    } else {
                        line += '<img src="http://placehold.it/65x65&text=' + artist.name + '" alt="' + artist.name +'" title="' + artist.name +'">';
                    }
                }
                lineup_html += line
            }
            lineup_html += '</ul>'
        }


        // var loader = '<hr><div class="festival-loader '+ this.slug +'"><i class="fa fa-refresh fa-spin fa-2x"></i><p>Loading more info...</p></div>';
        // boxText.innerHTML = header + dates + loader;
        boxText.innerHTML = header + dates + location + lineup_html;
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
            title: self.name + ' on ' + this.date.toDateString(),
            icon: icon_gig,
            map: google_map.map, // map is a global var initilized in the map binding 
            visible: false, 
            animation: google.maps.Animation.DROP
        });

        // Event listener for clicking marker
        google.maps.event.addListener(self.marker, 'click', function() {
            self.infobox.open(google_map.map, this);
            google_map.map.panTo(festLatLng);
        });

        // we need remove the boxText ko binding when the infobox closes

        // google.maps.event.addListener(self.infobox, 'closeclick', function() {
        //     ko.cleanNode(boxText);
        // });

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

        // Check if the user logged in
        if ($("#user_loggedin").length==1) {
            self.ifLoggedIn = ko.observable(true);
        } else {
            self.ifLoggedIn = ko.observable(false);
        }

        // Fesivals && events
        self.festivals = ko.observableArray();
        self.events = ko.observableArray(); //inside of the array, it's a object

        // Saved Maps
        self.saved_maps = ko.observableArray();
        self.selected_map = ko.observable();

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
        // self.bands = ko.observable(new Array());
        self.selected_genres_str = ko.observable();
        self.selected_genres = ko.observable(new Array());
        // self.genres = ko.observable(new Array());
        self.selected_countries_str = ko.observable();
        self.selected_countries = ko.observable(new Array());

        self.displayedFestivals = ko.computed(function() {
            // Represents a filtered list of festivals
            return ko.utils.arrayFilter(self.festivals(), function(festival) {
                var display_by_dates = false;
                var display_by_bands = false;
                var display_by_genres = false;
                var display_by_countries = false;

                // Filter by dates
                if ( (festival.start_date > self.min_date() && festival.start_date < self.max_date()) &&
                     (festival.end_date > self.min_date() && festival.end_date < self.max_date()) ) {
                    display_by_dates = true;
                }

                // Filter by countries
                if ( self.selected_countries().length == 0 ) {
                    display_by_countries = true;
                } else {
                    if ( self.selected_countries().indexOf(festival.country) != -1 ) {
                        display_by_countries = true;
                    }
                } 

                // Filter by bands
                if ( self.selected_bands().length == 0 ) {
                    display_by_bands = true;
                } else {
                    if ( ! festival.lineup ) {
                        display_by_bands = false;
                    } else {
                        // we have lineup info & user selected some bands
                        var found = false;
                        for ( var i in self.selected_bands() ) {
                            var band = self.selected_bands()[i];
                            if (festival.lineup.indexOf(band) == -1) {
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
                    if ( ! festival.genres ) {
                        display_by_genres = false;
                    } else {
                        // we have genre info & user selected some genres
                        var found = false;
                        for ( var i in self.selected_genres() ) {
                            var genre = self.selected_genres()[i];
                            if (festival.genres.indexOf(genre) == -1) {
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
                return display_by_dates && display_by_genres && display_by_bands && display_by_countries
            })

        }, this);
        
        self.selected_bands_str.subscribe(function(bands) {
            // Need to turn strings to the array
            if (bands) {
                if ( ! $('#reset_bands').is(":visible")) {
                    $('#reset_bands').show();
                }
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
                if ( $('#reset_bands').is(":visible")) {
                    $('#reset_bands').hide();
                }
            }
        });

        self.selected_bands2.subscribe(function(changes){
            var band = changes[0].value;
            // console.log(changes[0]);
            if (changes[0].status === "added") {
                // console.log(band + " is added");
                var data = {"artist": band};
                $.get("/metalmap/gigs/", data, function(returnedData) {
                    if (returnedData.length > 0 ) {
                        var mappedEvents = $.map(returnedData, function(item) { return new Gig(item) });
                        self.events.push({"band": band, "events": mappedEvents}) 
                    } 
                })
            } else {
                // console.log(band + " is removed");
                self.events.remove(function(item) { return item.band == band });
            }
        }, null, "arrayChange");


        self.selected_genres_str.subscribe(function(genres) {
            // Need to turn strings to the array
            if (genres) {
                if ( ! $('#reset_genres').is(":visible")) {
                    $('#reset_genres').show();
                }
                self.selected_genres(genres.split(','));
                // console.log(self.selected_genres());
            } else {
                // reset genres
                self.selected_genres([]);
                if ( $('#reset_genres').is(":visible")) {
                    $('#reset_genres').hide();
                }
            }
        });

        self.selected_countries_str.subscribe(function(countries) {
            // Need to turn strings to the array
            if (countries) {
                if ( ! $('#reset_countries').is(":visible")) {
                    $('#reset_countries').show();
                }
                self.selected_countries(countries.split(','));
                // console.log(self.selected_countries());
            } else {
                // reset countries
                self.selected_countries([]);
                if ( $('#reset_countries').is(":visible")) {
                    $('#reset_countries').hide();
                }
            }
        });


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


        // Control the displaying of events based on the array change
        self.events.subscribe(function(changes) {
             var changed_object = changes[0].value;
            if (changes[0].status === "added") {
                ko.utils.arrayForEach(changed_object.events, function(item) {
                    if ( (item.date > self.min_date() && item.date < self.max_date()) ) {
                        item.enableMarker();
                    } else {
                        item.disableMarker();
                    }
                });
            } else {
                ko.utils.arrayForEach(changed_object.events, function(item) {
                    item.disableMarker();
                });
            }
        }, null, "arrayChange");

        // Control the displaying of events based on the date range.
        self.date_range.subscribe(function (date_range) { 
            return ko.utils.arrayFilter(self.events(), function(band) {
                $.each(band.events, function(index, event){
                    if ( (event.date > self.min_date() && event.date < self.max_date()) ) {
                        event.enableMarker();
                    } else {
                        event.disableMarker();
                    }
                });
            }, this);
        });

        // Control the displaying of events based on country.
        self.selected_countries.subscribe(function(countries) {
            return ko.utils.arrayFilter(self.events(), function(band) {
                $.each(band.events, function(index, event){
                    if ( countries.length == 0 ) {
                        event.enableMarker();
                    } else {
                        if ( countries.indexOf(event.country) != -1 ) {
                            event.enableMarker();
                        } else {
                            event.disableMarker();
                        }
                    }
                });
            }, this);
            // console.log(countries);
        });

        // Load selected map
        self.selected_map.subscribe(function(map) {
            // Need to turn strings to the array
            console.log(map);
            var filters = JSON.parse(map.map_filters); 
            for (var type in filters) {
                console.log(type);
                // this.selected_bands_str("Arch Enemy");
                self['selected_' + type + '_str'](filters[type]);
                var type_array = filters[type].split(',');
                console.log(type_array);
                var new_array = new Array(type_array.length);
                // var new_array = [];
                for (i=0; i<type_array.length; i++) {
                    console.log(i + ": " + type_array[i]);
                    new_array[i] = {"id": type_array[i], "text": type_array[i]};
                }
                console.log(new_array);
                $('#' + type + '_selector').select2("data", new_array);
                console.log([{id: "Arch Enemy", text: "Arch Enemy"}, {id: "Deceased", text: "Deceased"}]);
            }
        });

        // Load initial festivals from server, convert it to Task instances, then populate self.festivals
        $.getJSON("/metalmap/all/?start_date=" + date_range.minDateStr + "&end_date=" + date_range.maxDateStr, function(data) {
            var festival_list = data['festivals']
            var mappedFestivals = $.map(festival_list, function(item) { return new Festival(item) });
            self.festivals(mappedFestivals);
            $("#loader").hide();
        });

        // Load saved map from server.
        $.getJSON("/profile/my_maps/", function(data) {
            for(var i = 0; i < data.length; i++) {
                var my_map = data[i];
                self.saved_maps.push(my_map);
                // console.log(my_map.title);
            }
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
                url: '/metalmap/artists/',
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
                url: '/metalmap/genres/',
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

        self.countryQuery = function (query) {
            $.ajax({
                url: '/metalmap/countries/',
                type: 'GET',
                dataType: 'json',
                data: {
                    search: query.term
                },
                success: function (data) {
                    var countries = [];
                    for ( i in data ) {
                        countries.push({id: data[i].name, text: data[i].name});
                    }
                    query.callback({
                        results: countries
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
        };

        self.submitReportForm = function (form) {
            var $form = $(form);

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
        };

        self.reset = function(type) {
            // make sure type is either bands or genres
            if ( type == 'bands' || type == 'genres' || type == 'countries') {
                // We use dictionary to call the observable so we can use variables there
                if ( self['selected_' + type + '_str']() ) {
                    self['selected_' + type + '_str']('');
                    $('#' + type + '_selector').select2("val", "");
                    $('#reset_' + type).hide();
                }
            } else {
                console.log("Nothing to reset, man.")
            }
        };
    }

    // This binding only control the initalization of the google map with all the festivals.
    ko.bindingHandlers.map = {
        init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
            var festivals = ko.utils.unwrapObservable(valueAccessor());
            // console.log("Custom binding init: " + festivals.length);
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
            } 
        }
    };

    // var viewModel = new FestivalMapViewModel();



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
                if ( clientWidth <= 640 ) {
                    $("#overlay").css("overflow-y", "scroll");
                    $(".hide-for-small-slideup").show();
                }
                $(element).animate({top: 0}, 600)
                $("#hide-overlay-button").show();
                $("#show-overlay-button").hide();
            } else {
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
    
    // date range bind
    ko.bindingHandlers.daterange = {
        init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
            // var today = new Date();
            console.log(date_range);
            console.log(viewModel);
            $(element).dateRangeSlider({
                bounds: {
                    // min: new Date(today.getFullYear(), 0, 1),
                    // max: new Date(today.getFullYear(), 11, 31)
                    min: date_range.minDate,
                    max: date_range.maxDate
                },
                defaultValues: {
                    // min: new Date(today.getFullYear(), 0, 1),
                    // max: new Date(today.getFullYear(), 11, 31)
                    min: date_range.minDate,
                    max: date_range.maxDate
                }
            }).on("valuesChanged", function(e, data){
                // viewModel.filterMarkersByDates(data.values.min, data.values.max);
                console.log(data);
                viewModel.min_date(new Date(data.values.min));
                viewModel.max_date(new Date(data.values.max));
            });

            //handle disposal (if KO removes by the template binding)
            // ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
            //     $(element).datepicker("destroy");
            // });
        }  
    };

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
        }
    ];

    FestivalMapViewModel.prototype.save = function() {
        var bands = this.selected_bands_str(); 
        var genres = this.selected_genres_str(); 
        var countries = this.selected_countries_str(); 
        if (bands || genres || countries) {
            var map_filters = {};
            if (bands) map_filters["bands"] = bands;
            if (genres) map_filters["genres"] = genres;
            if (countries) map_filters["countries"] = countries;
            $("#id_map_filters").val(JSON.stringify(map_filters));

            var $form = $("#save-form");

            if ( $form.valid() ) {
                // console.log("Form is valie, going to submit");
                var post_req = $.post( $form.attr("action"), $form.serialize() );

                post_req.done(function( data ) {
                    $("#id_title").val('');
                    if (data.status === "success") {
                        humane.info(data.message);
                    } else {
                        humane.error(data.message);
                    }
                });
            }

        }
    };

    FestivalMapViewModel.prototype.load = function() {
        this.selected_bands_str("Arch Enemy");
        $('#bands_selector').select2("data", [{id: "Arch Enemy", text: "Arch Enemy"}]);
    }

    return { viewModel: FestivalMapViewModel, template: mapTemplate };
});