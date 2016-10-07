'use strict';

/**
 * @ngdoc function
 * @name markovmutatorApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the markovmutatorApp
 */
angular.module('markovmutatorApp')
  .controller('MainCtrl', function ($scope, $http) ***REMOVED***
    $scope.genes = [];
    $scope.addGene = function() ***REMOVED***
      var url = JSON.stringify(document.querySelector("#url").value);
      $http.post('/addGene', url)
      .then(function successCallback(response) ***REMOVED***
        var gene = response.data;
        var duplicate_found = false;
        for(var i = 0; i < $scope.genes.length; i++) ***REMOVED***
          if (gene.source == $scope.genes[i].source && gene.document_id == $scope.genes[i].document_id) ***REMOVED***
            duplicate_found = true;
            break;
          ***REMOVED***
        ***REMOVED***
        if (!duplicate_found) ***REMOVED***
          $scope.genes.push(gene);
        ***REMOVED***
      ***REMOVED***, function errorCallback(response) ***REMOVED***
        console.log("Error\n" + response)
      ***REMOVED***);
  ***REMOVED***
  ***REMOVED***);
