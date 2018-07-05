var submitButton = document.getElementById('submit_button');
var vibrationSelect = document.getElementById('vibration_period');
var notAlertCheckbox = document.getElementById('not_alert');

function set_alert_value(vibration_period, not_alert, not_alert_start, not_alert_end) {
  if (not_alert == 'True') {
    $('#not_alert').prop("checked", true);
  } else {
    $('#not_alert').prop("checked", false);
  }

  $('#vibration_period').val(vibration_period);
  $('#not_alert').attr("checked", not_alert);
  $('#not_alert_start').val(not_alert_start);
  $('#not_alert_end').val(not_alert_end);
  
  if ($('#vibration_period').val() == 0) {
    hide_alert();
    return ;
  } 

  if ($('#not_alert').prop('checked') == true) {
    $('#not_alert_label').show();
    $('#not_alert_start_label').show();
    $('#not_alert_end_label').show();
  } else {
    $('#not_alert_label').show();
    $('#not_alert_start_label').hide();
    $('#not_alert_end_label').hide();
  }
}

function hide_alert() {
  $('#not_alert_label').hide();
  $('#not_alert_start_label').hide();
  $('#not_alert_end_label').hide();
}

function show_alert() {
  $('#not_alert_label').show();
  
  var notAlertChecked = $('#not_alert').prop('checked');
  if (notAlertChecked) {
    $('#not_alert_start_label').show();
    $('#not_alert_end_label').show();
  }
}


vibrationSelect.addEventListener('change', function() {
  var vibration_period = $('#vibration_period').val();
  if (vibration_period == '0') {
    hide_alert();
  } else {
    show_alert();
  }
});

notAlertCheckbox.addEventListener('change', function() {
  var notAlertChecked = $('#not_alert').prop('checked');
  if (notAlertChecked) {
    $('#not_alert_start_label').show();
    $('#not_alert_end_label').show();
  } else {
    $('#not_alert_start_label').hide();
    $('#not_alert_end_label').hide();
  }
});

submitButton.addEventListener('click', function() {
  // Some example configuration values
  var config = {
    'watchid': $.trim($('#watchid').text()),
    'city_name': $.trim($('#city_name').val()),
    'watch_style': $('#watch_style').val(),
    'vibration_period': $('#vibration_period').val(),
    'not_alert': $('#not_alert').prop('checked'),
    'not_alert_start': $('#not_alert_start').val(),
    'not_alert_end': $('#not_alert_end').val(),
    'invert_color': $('#invert_color').val(),
    'bluetooth_alert': $('#bluetooth_alert').prop('checked'),
    'watch_color': $('#watch_color').val()
  };

  $.ajax({ 
    type: "GET",
     url: "/webapp/chinaface_save?data=" + encodeURIComponent(JSON.stringify(config)),
    context: document.body, 
    success: function(){
      // Return data to watchapp
      location.href = 'pebblejs://close#' + 
      encodeURIComponent(JSON.stringify(config));
   }});
});