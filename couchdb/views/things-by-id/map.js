function(doc) {
    if(doc.type == 'thing') {
    	emit(doc._id, doc);
    }
}
