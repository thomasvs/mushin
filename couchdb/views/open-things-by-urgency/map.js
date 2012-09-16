function(doc) {
  if (doc.type == 'thing' && doc.complete != 100) {
    emit(doc.urgency, 1);
  }
}
