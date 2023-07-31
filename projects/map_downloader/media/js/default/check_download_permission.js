
lizMap.events.on({
	'uicreated': function(e) {
      var clone = $('#print-launch').clone();
      $('#print-launch').parent().append(clone);
      $('#print-launch').hide();
      clone.css('margin-top', 0);
      clone.click(function () {
        // Check if user can download the map
        clone.attr('disabled', true);
        $.get('/index.php/lizmap/member').then(function (data) {
          try {
            const allowed = data['allowed'];
            if (allowed) {
              clone.hide();
              $('#print-launch').show();
              $('#print-launch').click();
              let checkExist = setInterval(function() {
                 if (!$('#print-launch').hasClass('spinner')) {
                    clearInterval(checkExist);
                    clone.show();
                    $('#print-launch').hide();
                 }
              }, 100);
            } else {
              alert("You are not allowed to download maps anymore. Please upgrade to a membership.");
            }
          } catch (e) {
            console.error(e);
          }
          clone.attr('disabled', false);
        })
      })
	}
});