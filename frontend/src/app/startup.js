define(['jquery', 'knockout', './router', 'foundation', 'bootstrap', 'knockout-projections'], function($, ko, router) {

  // Non knockout stuff
  $(document).load(function() {
    $(this).foundation();
  });

  console.log("startup.js");

  // Components can be packaged as AMD modules, such as the following:
  ko.components.register('map', { require: 'components/map/map' });
  ko.components.register('nav-bar', { require: 'components/nav-bar/nav-bar' });
  ko.components.register('home-page', { require: 'components/home-page/home' });

  // ... or for template-only components, you can just point to a .html file directly:
  ko.components.register('about-page', {
    template: { require: 'text!components/about-page/about.html' }
  });

  // [Scaffolded component registrations will be inserted here. To retain this feature, don't remove this comment.]

  // Start the application
  ko.applyBindings({ route: router.currentRoute });


  // // date range bind
  // ko.bindingHandlers.daterange = {
  //     init: function(element) {
  //         var today = new Date();
  //         $(element).dateRangeSlider({
  //             bounds: {
  //                 min: new Date(today.getFullYear(), 0, 1),
  //                 max: new Date(today.getFullYear(), 11, 31)
  //             },
  //             defaultValues: {
  //                 // min: today,
  //                 min: new Date(today.getFullYear(), 0, 1),
  //                 max: new Date(today.getFullYear(), 11, 31)
  //             }
  //         }).on("valuesChanged", function(e, data){
  //             // viewModel.filterMarkersByDates(data.values.min, data.values.max);
  //             console.log(data);
  //             viewModel.min_date(new Date(data.values.min));
  //             viewModel.max_date(new Date(data.values.max));
  //         });

  //         //handle disposal (if KO removes by the template binding)
  //         // ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
  //         //     $(element).datepicker("destroy");
  //         // });
  //     }  
  // };
});
