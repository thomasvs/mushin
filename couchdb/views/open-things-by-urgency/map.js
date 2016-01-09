function(doc) {
  if (doc.type == 'thing' && doc.complete != 100 && doc.state != 2) {
    emit(doc.urgency, 1);
  }
}
