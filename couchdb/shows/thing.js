function(doc, req) {  
  // !json templates.thing
  // !json thing
  // !code vendor/couchapp/template.js
  // !code vendor/couchapp/path.js

  // we only show html
  return template(templates.thing, {
    thing : doc,
    start : doc.start,
    assets : assetPath(),
    editThingPath : showPath('edit', doc._id),
    index : listPath('index','recent-things',{descending:true, limit:5})
  });
}
