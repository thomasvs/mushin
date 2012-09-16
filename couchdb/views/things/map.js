function(doc) {
    if (doc.type == 'thing') {
    	emit(doc, 1);
    }
}
