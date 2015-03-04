// FIXME: something wrong in priority
// code vendor/couchapp/priority.js

function(doc) {
  if (doc.type == 'thing' && doc.state == 1 && doc.complete != 100) {
    emit(priority(doc), 1);
  }
}
