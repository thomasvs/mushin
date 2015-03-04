function(doc) {
    if (doc.type == 'thing' && doc.state == 1 && doc.complete != 100) {
        if (doc.projects) {
            doc.projects.forEach(function(project) {
                emit(project, 1);
            });
        }
    }
}
