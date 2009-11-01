function(doc) {
  if (doc.type == "thing") {
    emit(doc.start, {
      description : doc.description,
      start : doc.start,
      due : doc.due || null
    });    
  }
};
