function(doc) {
  if (doc.type == "thing" && doc.complete != 100 && doc.statuses) {
    doc.statuses.forEach(function (status) {
      emit(status, {
        title : doc.title,
        start : doc.start,
        due : doc.due || null
      });    
    });
  }
};
