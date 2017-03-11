function setState(event, state) {
  var bcm_id = event.target.name.substring(5,7);
  if (state) {
    var s = 1;
  }
  else {
    var s = 0;
  }
  $.getJSON( "/api/gpio/set/"+bcm_id+"/"+s, function( data ) {

  });
}

function setMode(mode, id) {
  $.getJSON( "/api/gpio/mode/"+id+"/"+mode, function( data ) {
    var gpio = $("#gp"+id);
    gpio.html(gpioRow(data));
    $("input[type=\"checkbox\"]").bootstrapSwitch();
    $("input[type=\"checkbox\"]").on('switchChange.bootstrapSwitch', setState);
  });
  return false;
};

function dropdownButton(label, id, dropdown) {
  var dt = '<div class="btn-group">';
  dt += '<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">';
  dt += label +  '<span class="caret"></span> </button>';
  dt += '<ul class="dropdown-menu">';

  $.each( dropdown, function(i, val) {
      dt += '<li><a href="#" onclick="return setMode(\'' + val[0] + '\', ' + id + ')">' + val[1] + '</a></li>';
  });
  dt += '</ul></div>';
  return dt;
};

function gpioRow(val) {
  var bcid = val["bcm_id"];

  var doc = "<div class=\"col-lg-1 col-md-1 col-sm-1 col-xs-1 gpio-cell\">";
  doc += "<strong>"+val["bcm_id"]+"</strong>";
  doc += "</div>";

  doc += "<div class=\"col-lg-2 col-md-2 col-sm-4 col-xs-4\">";
  doc += dropdownButton(val["mode"], bcid, [
    ['input', 'Input'],
    ['output', 'Output']
  ]);
  doc += "</div>";

  doc += "<div class=\"col-lg-2 col-md-2 col-sm-2 col-xs-4 gpio-cell\">";
  if (val["mode"] == "Input") {
    var state = "";
    switch (val["state"]) {
      case 0:
        state = "Low";
        break;
      case 1:
        state = "High";
        break;
      default:
        state = "Undefined";
    }
    doc += "<strong>Status: </strong>" +state;
  }
  else if (val["mode"] == "Output") {
    doc += "<strong>Status: </strong>";
    if (val["state"] == 1) {
      doc += '<input type="checkbox" data-size="mini" name="state'+bcid+'" checked>';
    }
    else {
      doc += '<input type="checkbox" data-size="mini" name="state'+bcid+'">';
    }
  }
  doc += "</div>";

  return doc;
};

function get_header() {
  $.getJSON( "/api/gpio", function( data ) {
    var gpiolist = $("#gpiolist");

    $.each( data["pins"], function(i, val) {
      var doc="<div class=\"row gpio\" id=\"gp"+val["bcm_id"]+"\">";
      doc += gpioRow(val);
      doc += "</div>";
      $(doc).appendTo(gpiolist);
    });

    $("input[type=\"checkbox\"]").bootstrapSwitch();
    $("input[type=\"checkbox\"]").on('switchChange.bootstrapSwitch', setState);
  });
}
