function box3dB(x, y, z, w, h, d, color, opacity) {
  layer = new Konva.Layer();

  var asp_y = d/5;
  var asp_x = asp_y/2;

  var back = new Konva.Line({
    points: [
      x, y+asp_y, 
      x+w+asp_x, y,
      x+w+asp_x, y+h-asp_y,
      x, y+h
    ],
    fill: color,
    opacity: opacity,
    stroke: 'black',
    strokeWidth: 1,
    closed : true
  });

  var right = new Konva.Line({
    points: [
      x+w+asp_x, y,
      x+w+d, y+asp_y,
      x+w+d, y+h,
      x+w+asp_x, y+h-asp_y
    ],
    fill: color,
    opacity: opacity,
    stroke: 'black',
    strokeWidth: 1,
    closed : true
  });

  var bottom = new Konva.Line({
    points: [
      x, y+h,
      x+w+asp_x, y+h-asp_y,
      x+w+d, y+h,
      x+d-asp_x, y+h+asp_y,
    ],
    fill: color,
    opacity: opacity,
    stroke: 'black',
    strokeWidth: 1,
    closed : true
  });


  layer.add(back);
  layer.add(right);
  layer.add(bottom);

  return layer;
}



function box3dF(x, y, z, w, h, d, color, opacity) {
  layer = new Konva.Layer();

  var asp_y = d/5;
  var asp_x = asp_y/2;

  var left = new Konva.Line({
    points: [
      x, y+asp_y,
      x+d-asp_x, y+asp_y+asp_y,
      x+d-asp_x, y+h+asp_y,
      x, y+h
    ],
    fill: color,
    opacity: opacity,
    stroke: 'black',
    strokeWidth: 1,
    closed : true
  });

  var front = new Konva.Line({
    points: [
      x+d-asp_x, y+asp_y+asp_y,
      x+w+d, y+asp_y,
      x+w+d, y+h,
      x+d-asp_x, y+h+asp_y
    ],
    fill: color,
    opacity: opacity,
    stroke: 'black',
    strokeWidth: 1,
    closed : true
  });

  var btop = new Konva.Line({
    points: [
      x, y+asp_y, 
      x+w+asp_x, y,
      x+w+d, y+asp_y,
      x+d-asp_x, y+asp_y+asp_y
    ],
    fill: color,
    opacity: opacity,
    stroke: 'black',
    strokeWidth: 1,
    closed : true
  });

  layer.add(left);
  layer.add(front);
  layer.add(btop);

  return layer;
}

function temp_to_color(temp) {
  if (temp > 0) {
    var thue = 0.8 - (temp/50);

    if (thue < 0.01) {
      thue = 0.01;
    }

    var color = tinycolor.fromRatio({h:thue, s:1, v:1}).toHexString();
  }
  else {
    var color = "#222222"
  }
  return color;
}

function draw_node(cluster, num, temp, cpu) {
  // Draw some boxes

  var pos = 4 - num;
  var y = pos * 60;

  cluster.add(box3dB(1, y, 1, 100, 80, 100, temp_to_color(temp), 0.5));

  //cluster.add(box3dB(30, y+40, 1, 30, 30, 30, temp_to_color(cpu), 1));
  cluster.add(box3dF(30, y+40, 1, 30, 30, 30, temp_to_color(cpu), 1));

  cluster.add(box3dF(1, y, 1, 100, 80, 100, temp_to_color(temp), 0.5));
}

function update_state() {
  $.getJSON( "/api/node/state/", function( data ) {
    var cluster = new Konva.Stage({
      container: 'cluster',
      width: 300,
      height: 300
    });

    $.each(data, function(i, val) {
      draw_node(cluster, val.node, val.temps.ambient, val.temps.cpu);
      $("#temp"+ val.node).text(val.temps.ambient);
      $("#cputemp"+ val.node).text(val.temps.cpu);
      if (val.state == 0) {
        $("#node" + val.node + "-stat-off").show();
        $("#node" + val.node + "-stat-startup").hide();
        $("#node" + val.node + "-stat-on").hide();
        $("#node" + val.node + "-off").hide();
        $("#node" + val.node + "-on").show();
      }
      if (val.state == 1) {
        $("#node" + val.node + "-stat-off").hide();
        $("#node" + val.node + "-stat-startup").show();
        $("#node" + val.node + "-stat-on").hide();
        $("#node" + val.node + "-off").show();
        $("#node" + val.node + "-on").hide();
      }
      if (val.state == 2) {
        $("#node" + val.node + "-stat-off").hide();
        $("#node" + val.node + "-stat-startup").hide();
        $("#node" + val.node + "-stat-on").show();
        $("#node" + val.node + "-off").show();
        $("#node" + val.node + "-on").hide();
      }
    });
  });

  $.getJSON( "/api/system/state/", function( data ) {
    if (data.powergood == false) {
      $("#power-standby").show();
      $("#power-active").hide();
      $("#main-on").show();
      $("#main-off").hide();
    } else {
      $("#power-standby").hide();
      $("#power-active").show();
      $("#main-on").hide();
      $("#main-off").show();
    };
  });
}

function node_on(node) {
  $.getJSON( "/api/node/on/"+node, function( data ) {})
};

function node_off(node) {
  $.getJSON( "/api/node/off/"+node, function( data ) {})
};

function atx_on() {
  $.getJSON( "/api/atx/on/", function( data ) {})
};

function atx_off() {
  $.getJSON( "/api/atx/off/", function( data ) {})
};

function main_screen() {
  update_state();
  setInterval(update_state, 3000);
};
