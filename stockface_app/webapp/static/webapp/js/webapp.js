var submitButton = document.getElementById('submit_button');
submitButton.addEventListener('click', function() {
  // Some example configuration values
  var config = {
    'watchid': $.trim($('#watchid').text()),
    'stock_code1': $.trim($('#stock_code1').val()),
    'stock_code2': $.trim($('#stock_code2').val()),
    'stock_code3': $.trim($('#stock_code3').val())
  };

  $.ajax({ 
  	type: "GET",
	url: "/webapp/save?data=" + encodeURIComponent(JSON.stringify(config)),
  	context: document.body, 
  	success: function(){
  		// Return data to watchapp
  		location.href = 'pebblejs://close#' + 
   		encodeURIComponent(JSON.stringify(config));
   }});

});