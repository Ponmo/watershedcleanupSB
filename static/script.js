$(document).ready(function(){ 
  $("#monthSelection").click(function() {
    if($("input.abc").not(":checked").length === 0)
    {
      $("#map").replaceWith("<p>Replaced</p>")
      var helloWorld = $('#map').html();
    }
    if($("#Jan").is(":checked"))
    {
    }
  }; 
});
