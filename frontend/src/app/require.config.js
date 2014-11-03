// require.js looks for the following global when initializing
var require = {
    baseUrl: ".",
    paths: {
        "bootstrap":            "bower_modules/components-bootstrap/js/bootstrap.min",
        "crossroads":           "bower_modules/crossroads/dist/crossroads.min",
        "hasher":               "bower_modules/hasher/dist/js/hasher.min",
        "modernizr":            "bower_modules/foundation/js/vendor/modernizr",
        // "jquery":               "bower_modules/jquery/dist/jquery",
        "jquery":               "bower_modules/foundation/js/vendor/jquery",
        "jquery-ui":            "lib/jquery-ui/js/jquery-ui-1.10.4.custom.min",
        "fastclick":            "bower_modules/foundation/js/vendor/fastclick",
        "foundation":           "bower_modules/foundation/js/foundation.min",
        "slider":               "lib/slider/jQDateRangeSlider-min",
        "select2":              "bower_modules/select2/select2",
        "underscore":           "lib/underscore/underscore-min",
        "mousewheel":           "lib/jScrollPane/jquery.mousewheel",
        "jscrollpane":          "lib/jScrollPane/jquery.jscrollpane.min",
        "humane":                "bower_modules/humane-js/humane.min",
        "validation":           "bower_modules/jquery.validation/dist/jquery.validate.min",
        "knockout":             "bower_modules/knockout/dist/knockout",
        "knockout-projections": "bower_modules/knockout-projections/dist/knockout-projections",
        "signals":              "bower_modules/js-signals/dist/signals.min",
        "text":                 "bower_modules/requirejs-text/text"
    },
    shim: {
        "bootstrap": { deps: ["jquery"] },
        "foundation": { deps: ["jquery", "modernizr", "fastclick"] },
        "jscrollpane": { deps: ["jquery", "mousewheel", "jquery-ui",] },
        "slider": { deps: ["jquery", "jquery-ui",] }
    }
};

/*
    {% compress js %}
        <script src="{{ STATIC_URL }}bower_components/foundation/js/vendor/modernizr.js"></script>
        <script src="{{ STATIC_URL }}bower_components/foundation/js/vendor/jquery.js"></script>
        <script src="{{ STATIC_URL }}js/lib/jquery-ui/js/jquery-ui-1.10.4.custom.min.js"></script>
        <script src="{{ STATIC_URL }}bower_components/foundation/js/vendor/fastclick.js"></script>
        <script src="{{ STATIC_URL }}bower_components/foundation/js/foundation.min.js"></script>
        <script src="{{ STATIC_URL }}bower_components/foundation/js/foundation.min.js"></script>
        <script src="{{ STATIC_URL }}js/lib/slider/jQDateRangeSlider-min.js" type="text/javascript"></script>
        <script src="{{ STATIC_URL }}bower_components/select2/select2.js"></script>
        <script src="{{ STATIC_URL }}js/lib/underscore/underscore-min.js" type="text/javascript"></script>
        <script src="{{ STATIC_URL }}js/lib/jScrollPane/jquery.mousewheel.js" type="text/javascript"></script>
        <script src="{{ STATIC_URL }}js/lib/jScrollPane/jquery.jscrollpane.min.js" type="text/javascript"></script>
        <script src="{{ STATIC_URL }}bower_components/humane-js/humane.min.js"></script>
        <script src="{{ STATIC_URL }}bower_components/jquery.validation/dist/jquery.validate.min.js"></script>
        <script src="{{ STATIC_URL }}js/app.js" type="text/javascript"></script>
    {% endcompress %}
*/