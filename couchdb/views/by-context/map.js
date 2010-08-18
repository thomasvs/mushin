function(doc) {
  if (doc.type == "thing" && doc.contexts) {
    doc.contexts.forEach(function (context) {
      emit(context, {
        title : doc.title,
        start : doc.start,
        due : doc.due || null
      });    
    });
  }
};
