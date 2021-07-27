$(document).ready(function() { 
  $(".Month").change(function() {
    if ($('.Month:checked').length == $('.Month').length) {
      $("#map").replaceWith("<iframe id='map' src='https://www.geosheets.com/map/s:KJV92kAM/cleanups/embed' class='map'></iframe>")
    }
    else if ($('.Month:checked').length === 0) {
      $("#map").replaceWith("<iframe id='map' src='https://www.geosheets.com/map/s:KJV92kAM/cleanups?filters=%7B%22a.%20Name%22%3A%22_all_%22%2C%22b.%20People%22%3A%22_all_%22%2C%22c.%20Date%22%3A%22_all_%22%2C%22d.%20Place(s)%22%3A%22_all_%22%2C%22e.%20Weight%20(lbs)%22%3A%22_all_%22%2C%22f.%20Bag(s)%22%3A%22_all_%22%2C%22g.%20Time%20(hrs)%22%3A%22_all_%22%7D' class='map'></iframe>")
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
