"use strict";
(() => {
  const search = document.querySelector("#search");
  const module = document.querySelector("#module");
  const normalize = value => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  if (search && module) {
    const filter = () => {
      let count = 0;
      document.querySelectorAll(".card").forEach(card => {
        const match = normalize(card.dataset.title + " " + card.dataset.module).includes(normalize(search.value.trim())) && (!module.value || card.dataset.module === module.value);
        card.hidden = !match;
        if (match) count++;
      });
      document.querySelector("#result-count").textContent = `${count} ${count === 1 ? "aula" : "aulas"}`;
      document.querySelector("#empty").hidden = count > 0;
    };
    search.addEventListener("input", filter);
    module.addEventListener("change", filter);
  }
  const notes = document.querySelector("#notes");
  if (!notes) return;
  const lesson = document.body.dataset.lesson;
  const key = "gml-262-notes-" + lesson;
  const status = document.querySelector("#save-status");
  try { notes.value = localStorage.getItem(key) || ""; }
  catch { status.textContent = "Armazenamento indisponível. Exporte para guardar."; }
  const save = () => {
    try { localStorage.setItem(key, notes.value); status.textContent = "Salvo neste navegador."; }
    catch { status.textContent = "Não foi possível salvar. Exporte seu caderno."; }
  };
  notes.addEventListener("input", save);
  document.querySelector("#export-notes").addEventListener("click", () => {
    const data = {schema: 1, course: "gml-262", lesson, notes: notes.value};
    const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], {type: "application/json"}));
    const link = document.createElement("a");
    link.href = url; link.download = `caderno-aula-${lesson.padStart(2, "0")}.json`;
    link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  document.querySelector("#import-notes").addEventListener("change", async event => {
    const file = event.target.files[0];
    if (!file) return;
    try {
      if (file.size > 2000000) throw new Error("too large");
      const data = JSON.parse(await file.text());
      if (data.schema !== 1 || data.course !== "gml-262" || String(data.lesson) !== lesson || typeof data.notes !== "string") throw new Error("invalid notebook");
      if (notes.value.trim() && !window.confirm("Substituir as anotações desta aula pelo arquivo importado?")) return;
      notes.value = data.notes; save();
    } catch { status.textContent = "Arquivo inválido ou pertencente a outra aula."; }
    event.target.value = "";
  });
})();
