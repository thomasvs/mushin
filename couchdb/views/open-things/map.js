function(doc) {
  if (doc.type == 'thing' && doc.complete != 100) {
    emit(doc.start, {
      description: doc.description,
      start: doc.start,
      due: doc.due || null
    });
  }
}
