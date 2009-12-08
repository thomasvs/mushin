// list all projects
// list takes a view that reduces to project, thing count

function(head, req) {
  // !json templates.projects
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
    send(template(templates.projects.head, {
      title : "Mushin Projects",
      newPostPath : showPath("edit"),
      index : indexPath,
      assets : assetPath()
    }));
    
    // loop over view rows, rendering one at a time
    var row, key;
    var things = 0, projects = 0;
    while (row = getRow()) {
      projects++;
      things += row.value;

        send(Mustache.to_html(templates.projects.row, {
        project: row.key,
	things: row.value,
        // FIXME: pretty ugly to take 1 as startkey and 3 as endkey for date,
        // but let's assume no medieval knights nor futuristic robots will
        // use this
        link: listPath('index','by-project', {
          startkey: [row.key, "3"],
          endkey: [row.key, "1"],
          title: "Things for project " + row.key,
          descending:true})
      }));        
    }
    
    // render the html tail template
    send('projects: ' + projects + '<br/>things: ' + things + '<br/>');
    send(template(templates.projects.tail, {
      assets : assetPath()
    }));
  });

};
