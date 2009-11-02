function(doc) {
  if (doc.type == "thing" && doc.complete != 100 && doc.due) {
    emit(doc.due, {
      description : doc.description,
      start : doc.start,
      due : doc.due || null
    });    
  }
};
