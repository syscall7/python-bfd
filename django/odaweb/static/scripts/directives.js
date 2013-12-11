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