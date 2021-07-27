$(document).ready(function(){ 
  $("#monthSelection").click(function() {
    $("#map").replaceWith("<p>Replaced</p>")
    if($("input.abc").not(":checked").length === 0)
    {
      var helloWorld = $('#map').html();
    }
    if($("#Jan").is(":checked"))
    {
    }
  }; 
});
