function(doc) {
  if (doc.type == "thing" && doc.start !== null) {
    emit(doc.start, {
      title : doc.title,
      start : doc.start,
      due : doc.due || null
    });    
  }
};
