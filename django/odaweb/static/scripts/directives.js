odaApplication.directive('slider', function ($parse) {
   return {
       restrict: 'A',
       link: function (scope, element, attrs) {
           var options = $parse(attrs.slider)(scope);

           $(element).slider(options);

           scope.$watch(attrs.slider, function(newValue, oldValue) {
                if (newValue) {
                    $(element).slider("destroy");
                    $(element).slider(newValue);
                }
            }, true);
       }
   };
});

odaApplication.directive('whenScrolled', function() {
   return {
      scope: {
        callback: '&whenScrolled'
      },
      link: function(scope, elm, attrs) {
        var raw = elm[0];

        elm.bind('scroll', function() {
            if (raw.scrollTop + raw.offsetHeight >= raw.scrollHeight) {
                //scope.$apply(attr.whenScrolled);
                scope.callback({mode:'UP'});
            }
        });
      }
   }
});
/*
odaApplication.directive('scroll', []).directive('whenScrolled', function() {
    return function(scope, elm, attr) {
        var raw = elm[0];

        elm.bind('scroll', function() {
            if (raw.scrollTop + raw.offsetHeight >= raw.scrollHeight) {
                scope.$apply(attr.whenScrolled);
            }
        });
    };
});
*/
odaApplication.directive('resize', function ($window) {
    return function (scope, element) {
        $(element).height($(window).height()-157);
    }
});

odaApplication.directive('popover', function ($parse) {
    return {
       restrict: 'A',
       link: function (scope, element, attrs) {
           var options = $parse(attrs.popover)(scope);

           $(element).popover(options);

       }
   };
});

odaApplication.directive('platformOption', function(odaApi){
    return {
       restrict: 'A',
       link: function (scope, element, attrs) {
           $(element).change(function(){

               var opts = $.map(
                    $('.platform-option-select'), function(v) {return $(v).val();}
                );

                opts = $.grep(opts, function(e) { return e != "DEFAULT"});

                form_data = {
                    options: opts,
                    arch : $('#select-live-architecture').val(),
                    base_address : $('#set-live-base-address').val(),
                    hex_val : $('#hex').val(),
                    endian : $('#hex-display .endian-select').val(),
                    disassemble: true
                };

                $.post('/odaweb/_set', form_data)
                    .done(function(response) {
                    //$('#hex-alert').hide();
                    //$('#live-mode-platform-options-form').html(response.form_html);
                    //Load(binary, true);
                    odaApi.updatePlatformOptions();
                }).fail(function(response){
                    $('#hex-alert').show();
                });


           });

       }
   };
});