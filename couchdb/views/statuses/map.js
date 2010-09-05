function(doc) {
    if (doc.type == 'thing' && doc.complete != 100) {
        if (doc.statuses) {
            doc.statuses.forEach(function(status) {
                emit(status, 1);
            });
        }
    }
}
