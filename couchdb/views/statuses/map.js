function(doc) {
    if (doc.type == 'thing' && doc.state == 1 && doc.complete != 100) {
        if (doc.statuses) {
            doc.statuses.forEach(function(status) {
                emit(status, 1);
            });
        }
    }
}
