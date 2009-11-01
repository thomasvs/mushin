function(doc) {
  if (doc.type == "thing" && doc.projects) {
    doc.projects.forEach(function (project) {
      emit([project, doc.start], {
        description : doc.description,
        start : doc.start,
        due : doc.due || null
      });    
    });
  }
};
