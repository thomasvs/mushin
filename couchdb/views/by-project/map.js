function(doc) {
  if (doc.type == 'thing' && doc.complete != 100 && doc.state != 2 && doc.projects) {
    doc.projects.forEach(function(project) {
      emit([project, doc.start], {
        title: doc.title,
        start: doc.start,
        due: doc.due || null
      });
    });
  }
}
