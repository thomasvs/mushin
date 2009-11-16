// this reduce reduces to a count of completed and total things per project
function(keys, values, rereduce) {
  completed = 0;
  priority = 0.0;
  id = "";
  title = "";

  if (rereduce) {
    total = 0;

    for (var i = 0; i < values.length; i++) {
      completed += values[i][0];
      total += values[i][1];
      if (values[i][2] > priority) {
        priority = values[i][2];
        id = values[i][3];
        title = values[i][4];
      }
    }

    return [completed, total, priority, id];
  } else {
    for (var i = 0; i < values.length; i++) {
      if (values[i][1] == 100) {
        completed += 1;
      }
      if (values[i][2] >= priority) {
        priority = values[i][2];
        id = values[i][3];
        title = values[i][4];
      }
    }
    return [completed, values.length, priority, id];
  }
}
