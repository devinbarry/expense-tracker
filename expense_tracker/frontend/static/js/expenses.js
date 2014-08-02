"use strict";

(function() {
    var app = angular.module("expenseManager.expenses", ["ui.bootstrap"]);
    var apiBase = '/api/v1/';

    app.config(function($httpProvider) {
        // Always send the standard header
        $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    });

    // Service provides RESTful methods to manage expenses on the server
    app.service('ExpenseService', ['$http', function($http) {
        var urlBase = apiBase + 'expense/';
        this.getExpenses = function(dates) {
            if (dates) {
                return $http.get(urlBase, {params:{date__range: [dates.from, dates.to]}});
            }
            return $http.get(urlBase);
        };
        this.getExpense = function(id) {
            return $http.get(urlBase + id + "/");
        };
        this.saveExpense = function(item) {
            return $http.post(urlBase, item);
        };
        this.deleteExpense = function(id) {
            return $http.delete(urlBase + id + "/");
        };
    }]);

    app.service('FilterService', ['$log', function($log) {
        var dates = {from: new Date(), to: new Date()};
        this.getFromDate = function () {
            var day = dates.from.getDate();
            var month = dates.from.getMonth() + 1;
            var year = dates.from.getFullYear();
            return year + "-" + month + "-" + day;
        };
        this.getToDate = function () {
            var day = dates.to.getDate();
            var month = dates.to.getMonth() + 1;
            var year = dates.to.getFullYear();
            return year + "-" + month + "-" + day;
        };
        this.getDates = function() {
            return dates;
        };
        this.setDates = function(newDates) {
            dates = newDates;
            //$log.info('Setting dates.from to: ' + this.getFromDate());
            //$log.info('Setting dates.to to: ' + this.getToDate());
        };
    }]);

    // Controller for expense list page
    app.controller('ExpenseListController', ['$scope', 'ExpenseService', 'FilterService',
        function($scope, ExpenseService, FilterService) {
            $scope.message = '';
            $scope.expenses = [];
            $scope.totals = {};

            // Get expenses, supplying the dates as a filter
            $scope.getFilteredExpenses = function() {
                ExpenseService.getExpenses(FilterService.getDates())
                    .success(function(expenses) {
                        $scope.expenses = expenses.objects;
                        $scope.totals = {amount: expenses.meta.total_amount, count: expenses.meta.total_count};
                    })
                    .error(function() {
                        $scope.message = "Unable to fetch expenses";
                    });
            };
            // Get all expenses, unfiltered
            $scope.getExpenses = function() {
                ExpenseService.getExpenses()
                    .success(function(expenses) {
                        $scope.expenses = expenses.objects;
                        $scope.totals = {amount: expenses.meta.total_amount, count: expenses.meta.total_count};
                    })
                    .error(function() {
                        $scope.message = "Unable to fetch expenses";
                    });
            };
            // Delete the selected expense
            $scope.deleteExpense = function(id) {
                ExpenseService.deleteExpense(id)
                    .success(function() {
                        $scope.message = "Expense has been successfully deleted";
                        $scope.expenses = $scope.getExpenses();
                    })
                    .error(function() {
                        $scope.message = "Expense could not be deleted";
                    });
            };
            $scope.getExpenses();
        }
    ]);

    // controller for the date pickers used for filtering the expense list
    app.controller('DatepickerExpenseListController', ['$scope', 'FilterService', function ($scope, FilterService) {
        $scope.today = function() {
            $scope.dt = {from: new Date(), to: new Date()};
            // From date is one month before current date
            $scope.dt.from.setMonth($scope.dt.from.getMonth() - 1)
            FilterService.setDates($scope.dt)
        };
        $scope.today();

        $scope.clear = function () {
            $scope.dt = null;
            FilterService.setDates($scope.dt)
        };

        $scope.open = function($event, name) {
            $event.preventDefault();
            $event.stopPropagation();
            if (name === 'to') {
                $scope.toOpened = true;
            }
            if (name === 'from') {
                $scope.fromOpened = true;
            }
            FilterService.setDates($scope.dt)
        };

        $scope.dateOptions = {
            formatYear: 'yy',
            startingDay: 1
        };

        $scope.initDate = new Date('2016-15-20');
        $scope.formats = ['dd-MMMM-yyyy', 'yyyy/MM/dd', 'dd.MM.yyyy', 'shortDate'];
        $scope.format = $scope.formats[2]; // Prefer to just show numbers
    }]);


    // Controller for expense detail (create + modify)
    app.controller('ExpenseFormController', ['$scope', '$routeParams', '$location', 'ExpenseService',
        function($scope, $routeParams, $location, ExpenseService) {
            $scope.expense = {};
            $scope.message = "";

            // =========================
            // Datepicker
            // =========================
            $scope.today = function() {
                $scope.expense.date = new Date();
            };
            $scope.clear = function () {
                $scope.expense.date = null;
            };
            $scope.open = function($event) {
                $event.preventDefault();
                $event.stopPropagation();
                $scope.dtOpened = true;
            };
            $scope.dateOptions = {
                formatYear: 'yy',
                startingDay: 1
            };
            $scope.initDate = new Date('2016-15-20');
            $scope.formats = ['dd-MMMM-yyyy', 'yyyy/MM/dd', 'dd.MM.yyyy', 'shortDate'];
            $scope.format = $scope.formats[2]; // Prefer to just show numbers

            // =========================
            // Expense Form
            // =========================
            if ($routeParams.id && $routeParams.id != "new") {
                // If an id was requested it's a modify, so fetch the expense and bind it to the form.
                ExpenseService.getExpense($routeParams.id)
                    .success(function(expense) {
                        $scope.expense = expense;
                        // Convert the string to a float so that the form can display it.
                        $scope.expense.amount = parseFloat(expense.amount);
                    });
            } else {
                $scope.today();
            }

            // A a method to create a new expense
            $scope.saveExpense = function() {
                ExpenseService.saveExpense($scope.expense)
                    .success(function() {
                        $location.path("/");
                    })
                    .error(function() {
                        $scope.message = "An error occurred while saving your item";
                    });
            };
        }
    ]);

})();

