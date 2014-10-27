define(["knockout", "text!./profile.html"], function(ko, profileTemplate) {

  function ProfileViewModel(route) {
    var self = this;
    self.profile_detail = ko.observable();
    $.get("/profile/", function(returnedData) {
        self.profile_detail(returnedData);
        // if (returnedData.length > 0 ) {
        //     var mappedEvents = $.map(returnedData, function(item) { return new Gig(item) });
        //     self.events.push({"band": band, "events": mappedEvents}) 
        // } 
    })
  }

  // HomeViewModel.prototype.doSomething = function() {
  //   this.message('You invoked doSomething() on the viewmodel.');
  // };

  return { viewModel: ProfileViewModel, template: profileTemplate };
});
