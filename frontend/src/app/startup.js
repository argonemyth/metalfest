define(['jquery', 'knockout', './router', './map', 'foundation', 'bootstrap', 'knockout-projections'], function($, ko, router, map) {

  // Non knockout stuff
  $(document).load(function() {
    $(this).foundation();
  });

  // Components can be packaged as AMD modules, such as the following:
  // ko.components.register('map', { require: 'components/map/map' });
  ko.components.register('nav-bar', { require: 'components/nav-bar/nav-bar' });
  ko.components.register('profile-page', { require: 'components/profile-page/profile' });

  // ... or for template-only components, you can just point to a .html file directly:
  ko.components.register('home-page', {
    template: { require: 'text!components/home-page/home.html'}
  });
  ko.components.register('about-page', {
    template: { require: 'text!components/about-page/about.html' }
  });

  // [Scaffolded component registrations will be inserted here. To retain this feature, don't remove this comment.]

  // Start the application
  ko.applyBindings(map.viewModel);
  // ko.applyBindings({route: router.currentRoute }, $('#page'));


});
