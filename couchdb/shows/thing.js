function(doc, req) {  
  // !json templates.thing
  // !json thing
  // !code vendor/couchapp/template.js
  // !code vendor/couchapp/path.js
  // !code vendor/mustache/mustache.js

 // FIXME: using a list to switch context in html to thing feels dirty
   return Mustache.to_html(templates.thing, {
     thing: [doc, ],
     title: doc.title,
     start: doc.start,
     due: doc.due,
     assets : assetPath(),
     editThingPath : showPath('edit', doc._id),
     index : listPath('index','recent-things',{descending:true, limit:5})
   });        
}
