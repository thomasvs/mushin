// all incomplete things that have a due date, ordered by due date
function(doc) {
  if (doc.type == 'thing' && doc.complete != 100 && doc.state == 1 && doc.due) {
    emit(doc.due, {
      description: doc.description,
      start: doc.start,
      due: doc.due
    });
  }
}
