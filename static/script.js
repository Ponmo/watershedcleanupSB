$(document).ready(function() { 
  $(".Month").change(function() {
    if ($('.Month:checked').length == $('.Month').length) {
      $("#map").replaceWith("<iframe id='map' src='https://www.geosheets.com/map/s:KJV92kAM/cleanups/embed' class='map'></iframe>")
    }
    else if ($('.Month:checked').length === 0) {
      alert("Please select at least one option");
    }
  });
  //$("#monthSelection").click(function() {
  //  if($("input.Month").not(":checked").length === 0)
  //  {
  //    $("#map").replaceWith("<p>All Checked</p>")
  //  }
  //  else if($("input.Month").not(":checked").length === 12)
  //  {
  //    $("#map").replaceWith("<p>All Not Checked</p>")
  //  }
  //  if($("#Jan").is(":checked"))
  //  {
  //  }
  //}); 
});
