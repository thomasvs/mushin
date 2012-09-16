// !code vendor/couchapp/priority.js

function(doc) {
  if (doc.type == 'thing' && doc.complete != 100) {
    emit(priority(doc), 1);
  }
}
