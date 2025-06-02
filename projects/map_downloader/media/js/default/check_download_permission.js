lizMap.events.on({
  'uicreated': function (e) {
    // If #print-launch is missing or empty, trigger print panel
    if ($('#print-launch').length === 0 || $.trim($('#print-launch').html()) === '') {
      $('#button-print').click();
    }

    const $original = $('#print-launch');

    if ($original.length === 0) {
      console.warn('#print-launch button not found even after clicking #button-print');
      return;
    }

    const $clone = $original.clone().attr('id', 'print-launch-clone');
    $original.parent().append($clone);
    $original.hide();
    $clone.css('margin-top', 0);

    $clone.on('click', function () {
      $clone.prop('disabled', true);

      $.get('/index.php/lizmap/member')
        .then(function (data) {
          try {
            const allowed = data?.allowed;
            const isAnonymous = data?.detail === "Authentication credentials were not provided.";

            if (allowed || isAnonymous) {
              if (isAnonymous) {
                console.warn("User is anonymous – allowing print by default.");
              }

              $clone.hide();
              $original.show().trigger('click');

              const checkExist = setInterval(function () {
                if (!$original.hasClass('spinner')) {
                  clearInterval(checkExist);
                  $clone.show();
                  $original.hide();
                }
              }, 100);
            } else {
              alert("You are not allowed to download maps anymore. Please upgrade to a membership.");
            }
          } catch (err) {
            console.error('Error processing member response:', err);
          }
          $clone.prop('disabled', false);
        })
        .fail(function () {
          console.error('Failed to contact /index.php/lizmap/member');
          $clone.prop('disabled', false);
        });
    });
  }
});
