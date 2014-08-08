"use strict";

(function() {
    var app = angular.module("expenseManager.weeklyTotal", []);
    var apiBase = '/api/v1/';

    app.config(function($httpProvider) {
        // Always send the standard header
        $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    });

    // Service provides RESTful methods to manage weekly totals on the server
    app.service('WeeklyTotalService', ['$http', function($http) {
        var urlBase = apiBase + 'weeklytotal/';
        this.getWeeklyTotals = function() {
            return $http.get(urlBase);
        };
    }]);

    // Controller for Weekly totals list
    app.controller('WeeklyTotalController', ['$scope', 'WeeklyTotalService',
        function($scope, WeeklyTotalService) {
            $scope.message = '';
            $scope.weeklyTotals = [];

            // Handle successful API call.
            var handleSuccess = function(weeklyTotals) {
                $scope.weeklyTotals = weeklyTotals.objects;
            };
            // Handle error condition after API call.
            var handleError = function() {
                $scope.message = "Unable to fetch weekly totals";
            };

            // Get all weekly totals, unfiltered
            $scope.getTotals = function() {
                WeeklyTotalService.getWeeklyTotals()
                    .success(handleSuccess)
                    .error(handleError);
            };
            $scope.getTotals();
        }
    ]);

})();

