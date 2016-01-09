function(doc) {
    if (doc.type == 'thing' && doc.state != 2 && doc.complete != 100) {
        if (doc.contexts) {
            doc.contexts.forEach(function(context) {
                emit(context, 1);
            });
        }
    }
}
