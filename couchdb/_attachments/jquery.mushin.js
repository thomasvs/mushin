// Licensed under the Apache License, Version 2.0 (the "License"); you may not
// use this file except in compliance with the License.  You may obtain a copy
// of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
// License for the specific language governing permissions and limitations under
// the License.

// Usage: The passed in function is called when the page is ready.
// MushinApp passes in the app object, which takes care of linking to 
// the proper database, and provides access to the MushinApp helpers.
// $.MushinApp(function(app) {
//    app.db.view(...)
//    ...
// });

// this needs vendor/couchapp/date.js loaded first

(function($) {

  function Design(db, name) {
    this.view = function(view, opts) {
      db.view(name+'/'+view, opts);
    };
  };

  var login;
  
  function init(app) {
    $(function() {
      // This function takes strings of the form 2009-11-21T22:49:58Z
      function prettyDate(time) {
      	var date = new Date().setRFC3339(time);
      	var diff = ((new Date()).getTime() - date.getTime()) / 1000;
      	var day_diff = Math.floor(diff / 86400);

      	return day_diff < -730 && Math.ceil(-day_diff / -365) + " years from now" ||
               day_diff < -45 && Math.ceil(-day_diff / 31) + " months from now" ||
               day_diff < -21 && Math.ceil(-day_diff / 7) + " weeks from now" ||
               day_diff < -1 && -day_diff + " days from now" ||
               day_diff == -1 && " tomorrow" ||
               day_diff < 0 && (
      	           diff < -86400 && Math.floor(-diff / 3600) + " hours from now" ||
                   diff < -7200 && "1 hour from now" ||
                   diff < -3600 && Math.floor(-diff / 60) + "minutes from now" ||
                   diff < -120 && "1 minute from now"
               ) ||
               day_diff < 1 && (
                   diff < 60 && "just now" ||
      	           diff < 120 && "1 minute ago" ||
      	           diff < 3600 && Math.floor(diff / 60) + " minutes ago" ||
      	           diff < 7200 && "1 hour ago" ||
      	           diff < 86400 && Math.floor(diff / 3600) + " hours ago"
                ) ||
      		day_diff == 1 && "yesterday" ||
      		day_diff < 21 && day_diff + " days ago" ||
      		day_diff < 45 && Math.ceil(day_diff / 7) + " weeks ago" ||
      		day_diff < 730 && Math.ceil(day_diff / 31) + " months ago" ||
      		Math.ceil(day_diff / 365) + " years ago";
      };
      
      app({
        prettyDate : prettyDate,
      });
    });
  };

  $.MushinApp = $.MushinApp || init;

})(jQuery);
