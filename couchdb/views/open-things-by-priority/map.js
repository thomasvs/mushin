// Lifted from
// http://bitbucket.org/benoitc/benoitcim/src/tip/vendor/inditeweb/date.js
// adapted to make the trailing Z optional, and remove fractional seconds
// Also see FIXME
Date.prototype.setRFC3339 = function(dString){
    //var regexp = /(\d\d\d\d)(-)?(\d\d)(-)?(\d\d)(T)?(\d\d)(:)?(\d\d)(:)?(\d\d)(\.\d+)?(Z|([+-])(\d\d)(:)?(\d\d))?/;
    var regexp = /(\d\d\d\d)(-)?(\d\d)(-)?(\d\d)(T)?(\d\d)(:)?(\d\d)(:)?(\d\d)?/;

    if (dString.toString().match(new RegExp(regexp))) {
        var d = dString.match(new RegExp(regexp));
        var offset = 0;

        this.setUTCDate(1);
        this.setUTCFullYear(parseInt(d[1],10));
        this.setUTCMonth(parseInt(d[3],10) - 1);
        this.setUTCDate(parseInt(d[5],10));
        this.setUTCHours(parseInt(d[7],10));
        this.setUTCMinutes(parseInt(d[9],10));
        this.setUTCSeconds(parseInt(d[11],10));
        //if (d[12])
        //    this.setUTCMilliseconds(parseFloat(d[12]) * 1000);
        //else
        //    this.setUTCMilliseconds(0);
        //if (d[13] != 'Z') {
        //    offset = (d[15] * 60) + parseInt(d[17],10);
        //    offset *= ((d[14] == '-') ? -1 : 1);
        //    this.setTime(this.getTime() - offset * 60 * 1000);
        //}
    } else {
        this.setTime(Date.parse(dString));
    }
    return this;
};

function(doc) {
  if (doc.type == "thing" && doc.complete != 100) {
    hours = (doc.time || 0) / 60. / 60.;
    effort = hours ? Math.max(1, Math.log(hours) / Math.log(3) + 1.0) : 0;

    // figure out pressure
    pressure = doc.urgency || 0;

    if (doc.due) {
      now = new Date();
      due = new Date().setRFC3339(doc.due);
      day = 60 * 60 * 24;
      // getTime returns in ms
      delta = ((due.getTime() - now.getTime()) / 1000);
      if (doc.time) { delta -= doc.time; }
      if (delta < 0) {
        pressure = 6; // overdue
      } else if (delta < day) {
        pressure = 5; // one day
      } else if (delta < 7 * day) {
        pressure = 4; // one week
      } else if (delta < 30 * day) {
        pressure = 3; // one month
      } else if (delta < 90 * day) {
        pressure = 2; // one quarter
      } else {
        pressure = 1; // more than a quarter
      }
    }

    // now calculate priority
    I = doc.importance || 0;
    P = Math.min((doc.urgency || 0) + 2, pressure)
    U = Math.max(doc.urgency || 0, P)
    E = effort;

    priority = Math.sqrt(2 * U * U + 2 * I * I + E * E) / Math.sqrt(5);

    emit(priority, 1);
  }
};
