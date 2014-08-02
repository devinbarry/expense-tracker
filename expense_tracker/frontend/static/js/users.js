"use strict";

(function() {
    var app = angular.module("expenseManager.users", []);
    var apiBase = '/api/v1/';

    app.config(function($httpProvider) {
        // Always send the standard header
        $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    });

    // Service provides RESTful methods to user entity against the server
    app.service('UserRestService', ['$http', function($http) {
        var urlBase = apiBase + 'user/';
        this.authenticate = function(user) {
            return $http.post(urlBase + "authenticate/", user);
        };
        this.register = function(user) {
            return $http.post(urlBase + "register/", user);
        };
    }]);

    // Service used to authenticate users against the server
    app.service('AuthenticationService', ['$location', '$http', '$q', 'UserService', 'UserRestService',
        function ($location, $http, $q, UserService, UserRestService) {
            // These error codes should have a 'reason' attached to the data
            var reason_error_codes = [400, 401, 403];

            // Generic error handler - returns a customised error handler
            var handleError = function(defaultMessage) {
                return function(response) {
                    if (reason_error_codes.indexOf(response.status) > -1) {
                        if (angular.isObject(response.data) && response.data.reason) {
                            return $q.reject(response.data.reason);

                        } else {
                            return $q.reject(defaultMessage);
                        }
                    } else {
                        if (angular.isObject(response.data) && response.data.error_message) {
                            return $q.reject(response.data.error_message);
                        } else {
                            return $q.reject("An unknown error occurred");
                        }
                    }
                };
            };
            // Customised error handlers
            var handleAuthError = handleError("Sorry, we're unable to authenticate you");
            var handleRegError = handleError("An error occurred while registering");

            var handleSuccess = function(response) {
                // Valid response returned means authentication was successful
                // Create an auth key and inject it into the $http singleton
                // so that all future requests will then be authorized
                var auth_key = response.data.username + ":" + response.data.api_key;
                $http.defaults.headers.common.Authorization = "ApiKey " + auth_key;
                UserService.setUser(response.data);
                $location.path("/");
            };

            this.authenticate = function (user) {
                return UserRestService.authenticate(user).then(handleSuccess, handleAuthError);
            };

            this.register = function(user) {
                return UserRestService.register(user).then(handleSuccess, handleRegError);
            };
        }
    ]);

    // Service used to fetch and set the currently logged in user (locally)
    app.service('UserService', ['$rootScope', function ($rootScope) {
        this.user = null;
        this.setUser = function (newUser) {
            this.user = newUser;
            // place the user on the root scope (this is used in app.run)
            $rootScope.user = this.user;
            // Tell all child scopes that the user has been changed
            $rootScope.$broadcast('setUserEvent');
        };
        this.getUser = function () {
            return this.user;
        };
    }]);

    // Controller that displays the logged in user and provides the logout function
    app.controller('UserDisplayController', ['$scope', '$location', '$http', 'UserService',
        function($scope, $location, $http, UserService) {
            this.username = null;
            this.getUserName = function() {
                var user = UserService.getUser();
                if (user != null) {
                    this.username = user.username;
                } else {
                    this.username = null;
                }
            };
            this.logout = function() {
                UserService.setUser(null);
                this.username = null;
                $http.defaults.headers.common.Authorization = null;
                $location.path("/login/");
            };
            var _this = this;
            $scope.$on('setUserEvent', function(event) {
                _this.getUserName();
            });
            this.getUserName();
        }
    ]);

    // Controller for the login page and the registration page - used to authenticate/register the user
    app.controller('UserController', ['AuthenticationService', function (AuthenticationService) {
        this.message = "";
        var _this = this;

        var updateMessage = function(message) {
            _this.message = message;
        };
        this.authenticate = function () {
            AuthenticationService.authenticate(this.user)
                // Only need to display the output if there was an error
                .catch(updateMessage);
        };
        this.register = function () {
            AuthenticationService.register(this.user)
                // Only need to display the output if there was an error
                .catch(updateMessage);
        };
    }]);
})();
