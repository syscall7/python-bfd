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