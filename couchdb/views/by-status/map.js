function(doc) {
  if (doc.type == "thing" && doc.statuses) {
    doc.statuses.forEach(function (status) {
      emit([status, doc.start], {
        title : doc.title,
        start : doc.start,
        due : doc.due || null
      });    
    });
  }
};
