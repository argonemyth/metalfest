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

  ProfileViewModel.prototype.signup = function() {
    // this.message('You invoked doSomething() on the viewmodel.');
    console.log("In signup function");
    $('#signin-form').hide();
    $('#signup-form').show();
    $('#signup-btn').hide();
    $('#signin-btn').show();
  };

  ProfileViewModel.prototype.signin = function() {
    // this.message('You invoked doSomething() on the viewmodel.');
    console.log("In signin function");
    $('#signup-form').hide();
    $('#signin-form').show();
    $('#signin-btn').hide();
    $('#signup-btn').show();
  };

  return { viewModel: ProfileViewModel, template: profileTemplate };
});
