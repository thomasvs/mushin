function(doc) {
  if (doc.type == 'thing' && doc.complete != 100 && doc.state == 1) {
    emit(doc.urgency, 1);
  }
}
