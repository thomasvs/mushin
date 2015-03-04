function(doc) {
    if (doc.type == 'thing' && doc.state == 1 && doc.complete != 100) {
        if (doc.contexts) {
            doc.contexts.forEach(function(context) {
                emit(context, 1);
            });
        }
    }
}
