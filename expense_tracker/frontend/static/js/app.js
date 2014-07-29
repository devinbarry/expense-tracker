"use strict";

(function() {
    var app = angular.module("expenseManager", ["ngRoute", "expenseManager.users", "expenseManager.expenses"]);

    app.config(function($httpProvider) {
        // Always send the standard header
        $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    });

    // Handles routing
    app.config(function($routeProvider) {
        $routeProvider
            .when("/", {
                controller: "ExpenseListController",
                templateUrl:"/static/partials/expense_list.html"
            })
            .when("/login/", {
                controller: "UserController",
                controllerAs: "auth",
                templateUrl:"/static/partials/login.html"
            })
            .when("/register/", {
                controller: "UserController",
                controllerAs: "registration",
                templateUrl:"/static/partials/registration.html"
            })
            .when("/expense/:id/", {
                controller: "ExpenseFormController",
                templateUrl:"/static/partials/expense_form.html"
            })
            .when("/expense/:id/delete/", {
                controller: "ExpenseFormController",
                templateUrl:"/static/partials/expense_form.html"
            })
            .otherwise({redirectTo: "/"})
    });

    // Send all view requests to login if user is not authenticated
    app.run(function($rootScope, $location) {
        // register listener to watch route changes
        $rootScope.$on("$routeChangeStart", function(event, next, current) {
            if ($rootScope.user == null) {
                if (next.templateUrl != "/static/partials/login.html" && next.controller != "UserController") {
                    $location.path( "/login/" );
                }
            }
        });
     });

})();

