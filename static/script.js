$(document).ready(function(){ 
  $("#monthSelection").click(function() {
    if($("input.Month").not(":checked").length === 0)
    {
      $("#map").replaceWith("<p>All Checked</p>")
    }
    else if($("input.Month").not(":checked").length === 12)
    {
      $("#map").replaceWith("<p>All Not Checked</p>")
    }
    if($("#Jan").is(":checked"))
    {
    }
  }); 
});
