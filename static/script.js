$(document).ready(function() { 
  $('#myModal').modal('show');
  $("#reports").hide();
  $("#legend").hide();
  $("#legend-embed").hide();
  $("#resolve").hide();
  $("#resolve-switch").hide();
  $("#map-reports").fadeOut(500)
  $(".Month").change(function() {
    if ($(".Month:checked").length == $(".Month").length) {
      $("#map-cleanups").replaceWith("<iframe id='map-cleanups' src='https://www.geosheets.com/map/s:DJj8Kv6R/cleanups/embed' class='map'></iframe>")
    }
    else if ($(".Month:checked").length === 0) {
      $("#map-cleanups").replaceWith("<iframe id='map-cleanups' src='https://www.geosheets.com/map/s:DJj8Kv6R/cleanups?filters=%7B%22Month%22%3A%5B%22None%22%5D%2C%22a.%20Name%22%3A%22_all_%22%2C%22b.%20People%22%3A%22_all_%22%2C%22c.%20Date%22%3A%22_all_%22%2C%22d.%20Place(s)%22%3A%22_all_%22%2C%22e.%20Weight%20(lbs)%22%3A%22_all_%22%2C%22f.%20Bag(s)%22%3A%22_all_%22%2C%22g.%20Time%20(hrs)%22%3A%22_all_%22%7D' class='map'></iframe>")
    }
    else {
      var baseLink = "https://www.geosheets.com/map/s:DJj8Kv6R/cleanups?filters=%7B%22Month%22%3A%5B"
      var first = true;
      if ($("#January").is(":checked")) {
        baseLink += "%22January%22"
        first = false;
      }
      if ($("#February").is(":checked")) {
        if (first == true) {
          baseLink += "%22February%22"
          first = false;
        }
        else {
          baseLink += "%2C%22February%22"
        }
      }
      if ($("#March").is(":checked")) {
        if (first == true) {
          baseLink += "%22March%22"
          first = false;
        }
        else {
          baseLink += "%2C%22March%22"
        }
      }
      if ($("#April").is(":checked")) {
        if (first == true) {
          baseLink += "%22April%22"
          first = false;
        }
        else {
          baseLink += "%2C%22April%22"
        }
      }
      if ($("#May").is(":checked")) {
        if (first == true) {
          baseLink += "%22May%22"
          first = false;
        }
        else {
          baseLink += "%2C%22May%22"
        }
      }
      if ($("#June").is(":checked")) {
        if (first == true) {
          baseLink += "%22June%22"
          first = false;
        }
        else {
          baseLink += "%2C%22June%22"
        }
      }
      if ($("#July").is(":checked")) {
        if (first == true) {
          baseLink += "%22July%22"
          first = false;
        }
        else {
          baseLink += "%2C%22July%22"
        }
      }
      if ($("#August").is(":checked")) {
        if (first == true) {
          baseLink += "%22August%22"
          first = false;
        }
        else {
          baseLink += "%2C%22August%22"
        }
      }
      if ($("#September").is(":checked")) {
        if (first == true) {
          baseLink += "%22September%22"
          first = false;
        }
        else {
          baseLink += "%2C%22September%22"
        }
      }
      if ($("#October").is(":checked")) {
        if (first == true) {
          baseLink += "%22October%22"
          first = false;
        }
        else {
          baseLink += "%2C%22October%22"
        }
      }
      if ($("#November").is(":checked")) {
        if (first == true) {
          baseLink += "%22November%22"
          first = false;
        }
        else {
          baseLink += "%2C%22November%22"
        }
      }
      if ($("#December").is(":checked")) {
        if (first == true) {
          baseLink += "%22December%22"
          first = false;
        }
        else {
          baseLink += "%2C%22December%22"
        }
      }
      baseLink += "%5D%2C%22a.%20Name%22%3A%22_all_%22%2C%22b.%20People%22%3A%22_all_%22%2C%22c.%20Date%22%3A%22_all_%22%2C%22d.%20Place(s)%22%3A%22_all_%22%2C%22e.%20Weight%20(lbs)%22%3A%22_all_%22%2C%22f.%20Bag(s)%22%3A%22_all_%22%2C%22g.%20Time%20(hrs)%22%3A%22_all_%22%7D"
      $("#map-cleanups").replaceWith("<iframe id='map-cleanups' src='" + baseLink + "' class='map'></iframe>")
    }
  });
  $("#switcher-1").change(function() {
    if ($("#switcher-1").is(':checked')) {
      $("#cleanups").show();  // checked
      $("#reports").hide();
      $("#map-reports").hide();
      $("#map-cleanups").show();
      $("#legend").hide();
      $("#legend-embed").hide();
      $("#legend-main").show();
      $("#legend-main-embed").show();
      $("#credit").show();
    }
    else {
      $("#cleanups").hide();  // unchecked
      $("#reports").show();
      $("#map-reports").show();
      $("#map-cleanups").hide();
      $("#legend").show();
      $("#legend-embed").show();
      $("#legend-main").hide();
      $("#legend-main-embed").hide();
      $("#credit").hide();
    }
  });
  $("#report-switch").click(function() {
    document.getElementById("replaceable").innerHTML = "Resolve a Location";
    $("#report").hide();
    $("#report-limit").hide();
    $("#report-switch").hide();
    $("#resolve").show();
    $("#resolve-switch").show();
  });
  $("#resolve-switch").click(function() {
    document.getElementById("replaceable").innerHTML = "Trash Report";
    $("#report").show();
    $("#report-limit").show();
    $("#report-switch").show();
    $("#resolve").hide();
    $("#resolve-switch").hide();
  });
});
