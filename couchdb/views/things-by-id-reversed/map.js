function(doc) {
    if (doc.type == 'thing') {
        emit(doc._id.split('').reverse().join(''), null);
        // emit(doc._id.split("").reverse(), null);
    }
}
