function(head, req) {
  // !json templates.index
  // !json thing
  // !code vendor/couchapp/path.js
  // !code vendor/couchapp/date.js
  // !code vendor/couchapp/template.js
  // use different templating language instead:
  // !code vendor/mustache/mustache.js

  var indexPath = listPath('index','recent-things',{descending:true, limit:5});

  // The provides function serves the format the client requests.
  // The first matching format is sent, so reordering functions changes 
  // thier priority. In this case HTML is the preferred format, so it comes first.
  provides("html", function() {
    // render the html head using a template
    send(template(templates.index.head, {
      title : req.query.title || "GTD",
      newPostPath : showPath("edit"),
      index : indexPath,
      assets : assetPath()
    }));
    
    // loop over view rows, rendering one at a time
    var row, key;
    while (row = getRow()) {
      var thing = row.value;

      var notempty = function () {
          return thing.due !== null;
      };

      key = row.key;
      send(Mustache.to_html(templates.index.row, {
        title : thing.title || "",
        start : thing.start,
        due : thing.due || null,
        notempty : notempty,
        link : showPath('thing', row.id)
      }));        
    }
    
    // render the html tail template
    send(template(templates.index.tail, {
      assets : assetPath()
    }));
  });

};
