// Shared behavior for study pages: remembers which self-test questions were answered
// without peeking, and shows that progress on the hub. Storage is a convenience only;
// every page must work when it is unavailable (private window, file:// restrictions).
(function () {
  "use strict";

  var PREFIX = "llm-study:";

  function load(lesson) {
    try {
      return JSON.parse(localStorage.getItem(PREFIX + lesson)) || [];
    } catch (err) {
      return [];
    }
  }

  function save(lesson, ids) {
    try {
      localStorage.setItem(PREFIX + lesson, JSON.stringify(ids));
    } catch (err) {
      /* storage unavailable: progress simply does not persist */
    }
  }

  // Lesson page: <body data-lesson="aula-01"> with <details class="q" id="q1"> blocks.
  var lesson = document.body.dataset.lesson;
  if (lesson) {
    var done = load(lesson);
    var questions = document.querySelectorAll("details.q[id]");
    var counter = document.querySelector("[data-quiz-progress]");

    var render = function () {
      if (counter) {
        counter.textContent = done.length + " de " + questions.length + " sem olhar a resposta";
      }
    };

    questions.forEach(function (q) {
      var label = document.createElement("label");
      var box = document.createElement("input");
      box.type = "checkbox";
      box.id = lesson + "-" + q.id + "-ok";
      box.checked = done.indexOf(q.id) !== -1;
      box.addEventListener("change", function () {
        done = done.filter(function (id) {
          return id !== q.id;
        });
        if (box.checked) {
          done.push(q.id);
        }
        save(lesson, done);
        render();
      });
      label.appendChild(box);
      label.appendChild(document.createTextNode("Acertei antes de abrir"));
      q.querySelector(".answer").appendChild(label);
    });
    render();
  }

  // Hub: <span data-progress-for="aula-01" data-total="8"></span>
  document.querySelectorAll("[data-progress-for]").forEach(function (el) {
    var count = load(el.dataset.progressFor).length;
    if (count > 0) {
      el.textContent = "autoteste " + count + "/" + el.dataset.total;
    }
  });
})();
