// FIXME: something wrong in priority
// code vendor/couchapp/priority.js

function(doc) {
    if (doc.type == 'thing') {
        if (doc.projects) {
            doc.projects.forEach(function(project) {
                emit(project, [
                    doc.time || 0,
                    doc.complete || 0,
                    priority(doc),
                    doc._id,
                    doc.title]);
            });
        }
    }
}
