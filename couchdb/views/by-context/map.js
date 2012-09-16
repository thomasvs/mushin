function(doc) {
  if (doc.type == 'thing' && doc.complete != 100 && doc.contexts) {
    doc.contexts.forEach(function(context) {
      emit([context, doc.start], {
        title: doc.title,
        start: doc.start,
        due: doc.due || null
      });
    });
  }
}
