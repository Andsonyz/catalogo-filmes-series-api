(() => {
  "use strict";
  const el = (id) => document.getElementById(id);
  const urls = { titulos: document.body.dataset.titulosUrl, generos: document.body.dataset.generosUrl };
  const state = { titulos: [], generos: [], editing: null, loaded: false, busy: false, genreBusy: false };
  const form = el("titulo-form");
  const fields = ["nome", "tipo", "genero", "numero_temporadas"];
  const csrf = form.querySelector("[name=csrfmiddlewaretoken]").value;

  class APIError extends Error {
    constructor(message, fields = {}) { super(message); this.fields = fields; }
  }

  async function request(url, { method = "GET", data } = {}) {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 15000);
    try {
      const response = await fetch(url, {
        method,
        credentials: "same-origin",
        signal: controller.signal,
        headers: { "Accept": "application/json", ...(data ? { "Content-Type": "application/json" } : {}), ...(method !== "GET" ? { "X-CSRFToken": csrf } : {}) },
        body: data ? JSON.stringify(data) : undefined,
      });
      let body = null;
      if (response.status !== 204) {
        try { body = await response.json(); } catch { /* A proxy/server may return HTML on failure. */ }
      }
      if (!response.ok) {
        const message = body?.detail || (response.status === 403
          ? "A operação não foi autorizada. Atualize a página e tente novamente."
          : `Não foi possível concluir a operação (HTTP ${response.status}).`);
        throw new APIError(message, body || {});
      }
      if (response.status !== 204 && !body) throw new APIError("O servidor enviou uma resposta inesperada. Tente novamente.");
      return body;
    } catch (error) {
      if (error instanceof APIError) throw error;
      throw new APIError("Não foi possível conectar ao servidor. Confira sua conexão e tente novamente. Seus dados continuam preenchidos.");
    } finally { window.clearTimeout(timeout); }
  }

  function message(text, error = false) {
    el("mensagem").textContent = text;
    el("mensagem").classList.toggle("error", error);
    el("mensagem").hidden = !text;
  }

  function clearErrors() {
    for (const name of fields) {
      el(name).removeAttribute("aria-invalid");
      el(`erro-${name}`).hidden = true;
      el(`erro-${name}`).textContent = "";
    }
    el("erro-formulario").hidden = true;
  }

  function showErrors(error) {
    let first = null;
    for (const name of fields) {
      const errors = error.fields[name];
      if (!errors) continue;
      // If a hidden field has an API error, reveal it so the error is reachable.
      if (name === "numero_temporadas") el("campo-temporadas").hidden = false;
      el(name).setAttribute("aria-invalid", "true");
      el(`erro-${name}`).textContent = Array.isArray(errors) ? errors.join(" ") : String(errors);
      el(`erro-${name}`).hidden = false;
      first ||= el(name);
    }
    el("erro-formulario").textContent = error.fields.non_field_errors?.join(" ") || (first ? "Confira os campos indicados. O título não foi salvo." : error.message);
    el("erro-formulario").hidden = false;
    first?.focus();
  }

  function syncSeasons() {
    const serie = el("tipo").value === "serie";
    el("campo-temporadas").hidden = !serie;
    el("numero_temporadas").required = serie;
    el("numero_temporadas").disabled = !serie;
  }

  function renderGenres(selected = el("genero").value) {
    el("genero").replaceChildren(new Option(state.generos.length ? "Selecione um gênero" : "Cadastre um gênero para começar", ""));
    for (const genero of state.generos) el("genero").add(new Option(genero.nome, String(genero.id)));
    el("genero").value = String(selected);
  }

  function renderTitles() {
    el("total-titulos").textContent = state.titulos.length;
    el("total-filmes").textContent = state.titulos.filter((t) => t.tipo === "filme").length;
    el("total-series").textContent = state.titulos.filter((t) => t.tipo === "serie").length;
    const genreNames = new Map(state.generos.map((g) => [g.id, g.nome]));
    const list = el("lista-titulos");
    list.replaceChildren();
    el("catalogo-vazio").hidden = state.titulos.length !== 0;
    for (const titulo of state.titulos) {
      const node = el("titulo-template").content.cloneNode(true);
      const card = node.querySelector("li");
      card.dataset.id = titulo.id;
      const serie = titulo.tipo === "serie";
      node.querySelector("h3").textContent = titulo.nome;
      node.querySelector(".art-label").textContent = serie ? "EM EPISÓDIOS" : "EM UM FILME";
      node.querySelector(".art-symbol").textContent = serie ? "S" : "F";
      node.querySelector(".art-id").textContent = `#${String(titulo.id).padStart(2, "0")}`;
      node.querySelector(".type-badge").textContent = serie ? "Série" : "Filme";
      node.querySelector(".title-seasons").textContent = serie ? `${titulo.numero_temporadas} ${titulo.numero_temporadas === 1 ? "temporada" : "temporadas"}` : "";
      node.querySelector(".title-genre").textContent = genreNames.get(titulo.genero) || "Gênero indisponível";
      const edit = node.querySelector(".edit-title");
      const remove = node.querySelector(".delete-title");
      edit.setAttribute("aria-label", `Editar ${titulo.nome}`);
      remove.setAttribute("aria-label", `Excluir ${titulo.nome}`);
      edit.addEventListener("click", () => editTitle(titulo));
      remove.addEventListener("click", () => deleteTitle(titulo));
      edit.disabled = remove.disabled = state.busy;
      list.append(node);
    }
  }

  function busy(value) {
    state.busy = value;
    el("titulo-campos").disabled = value || !state.loaded;
    el("adicionar-titulo").disabled = value;
    document.querySelectorAll(".edit-title,.delete-title").forEach((button) => { button.disabled = value; });
    el("salvar-titulo").textContent = value ? "Salvando…" : state.editing ? "Salvar alterações" : "Adicionar ao catálogo";
  }

  function resetForm(focus = false) {
    if (state.busy) return;
    state.editing = null;
    form.reset();
    clearErrors();
    syncSeasons();
    el("form-title").textContent = "Adicionar título";
    el("form-modo").textContent = "NOVA HISTÓRIA";
    el("form-description").textContent = "Mais uma história para a sua coleção.";
    el("salvar-titulo").textContent = "Adicionar ao catálogo";
    el("cancelar-edicao").hidden = true;
    if (focus) { el("nome").focus(); el("nome").scrollIntoView({ block: "center", behavior: "smooth" }); }
  }

  function editTitle(titulo) {
    if (state.busy) return;
    state.editing = { ...titulo };
    clearErrors();
    for (const name of fields) el(name).value = titulo[name] ?? "";
    syncSeasons();
    el("form-title").textContent = "Editar título";
    el("form-modo").textContent = `EM EDIÇÃO · #${titulo.id}`;
    el("form-description").textContent = "Dê um novo capítulo a essa história.";
    el("salvar-titulo").textContent = "Salvar alterações";
    el("cancelar-edicao").hidden = false;
    el("nome").focus();
    el("nome").scrollIntoView({ block: "center", behavior: "smooth" });
  }

  async function load() {
    el("colecao").setAttribute("aria-busy", "true");
    el("carregando").hidden = false;
    el("falha-carregamento").hidden = true;
    el("catalogo-vazio").hidden = true;
    el("lista-titulos").hidden = true;
    try {
      const [titulos, generos] = await Promise.all([request(urls.titulos), request(urls.generos)]);
      if (!Array.isArray(titulos) || !Array.isArray(generos)) throw new APIError("O servidor retornou uma lista inesperada.");
      state.titulos = titulos; state.generos = generos; state.loaded = true;
      renderGenres(); renderTitles();
      el("lista-titulos").hidden = false;
      busy(false);
    } catch (error) {
      el("erro-carregamento").textContent = error.message;
      el("falha-carregamento").hidden = false;
    } finally {
      el("carregando").hidden = true;
      el("colecao").setAttribute("aria-busy", "false");
    }
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (state.busy || !state.loaded || !form.reportValidity()) return;
    clearErrors(); message("");
    const editing = state.editing;
    const data = { nome: el("nome").value, tipo: el("tipo").value, genero: Number(el("genero").value), numero_temporadas: el("tipo").value === "filme" ? null : Number(el("numero_temporadas").value) };
    if (editing) {
      // PATCH only changed values; a series → film always clears seasons explicitly.
      for (const name of fields) if (data[name] === editing[name]) delete data[name];
      if (editing.tipo === "serie" && el("tipo").value === "filme") data.numero_temporadas = null;
    }
    busy(true);
    try {
      const saved = await request(editing ? `${urls.titulos}${editing.id}/` : urls.titulos, { method: editing ? "PATCH" : "POST", data });
      state.titulos = editing ? state.titulos.map((t) => t.id === saved.id ? saved : t) : [...state.titulos, saved];
      busy(false); resetForm(); renderTitles();
      message(editing ? `“${saved.nome}” foi atualizado.` : `“${saved.nome}” foi adicionado ao catálogo.`);
      el("colecao").focus();
    } catch (error) {
      busy(false); showErrors(error);
    }
  });

  async function deleteTitle(titulo) {
    if (state.busy || !window.confirm(`Excluir “${titulo.nome}”? Esta ação não pode ser desfeita.`)) return;
    busy(true); message("");
    try {
      await request(`${urls.titulos}${titulo.id}/`, { method: "DELETE" });
      state.titulos = state.titulos.filter((t) => t.id !== titulo.id);
      busy(false);
      if (state.editing?.id === titulo.id) resetForm();
      renderTitles(); message(`“${titulo.nome}” foi excluído.`);
      el("colecao").focus();
    } catch (error) { busy(false); message(error.message, true); }
  }

  const dialog = el("genero-dialog");
  el("abrir-genero").addEventListener("click", () => { dialog.showModal(); el("genero-nome").focus(); });
  for (const id of ["fechar-genero", "cancelar-genero"]) el(id).addEventListener("click", () => { if (!state.genreBusy) dialog.close(); });
  dialog.addEventListener("cancel", (event) => { if (state.genreBusy) event.preventDefault(); });
  el("genero-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (state.genreBusy || !event.target.reportValidity()) return;
    state.genreBusy = true;
    el("erro-genero-nome").hidden = el("erro-genero-formulario").hidden = true;
    el("genero-nome").removeAttribute("aria-invalid");
    el("salvar-genero").disabled = true; el("salvar-genero").textContent = "Criando…";
    try {
      const genero = await request(urls.generos, { method: "POST", data: { nome: el("genero-nome").value } });
      state.generos.push(genero); renderGenres(genero.id);
      el("genero-form").reset(); dialog.close();
      message(`Gênero “${genero.nome}” criado. Você já pode usá-lo no título.`);
      el("genero").focus();
    } catch (error) {
      if (error.fields.nome) {
        el("erro-genero-nome").textContent = [].concat(error.fields.nome).join(" ");
        el("erro-genero-nome").hidden = false;
        el("genero-nome").setAttribute("aria-invalid", "true");
      }
      el("erro-genero-formulario").textContent = error.fields.nome ? "Confira o nome do gênero. Os dados não foram salvos." : error.message;
      el("erro-genero-formulario").hidden = false; el("genero-nome").focus();
    } finally {
      state.genreBusy = false;
      el("salvar-genero").disabled = false; el("salvar-genero").textContent = "Criar gênero";
    }
  });

  el("tipo").addEventListener("change", syncSeasons);
  el("adicionar-titulo").addEventListener("click", () => resetForm(true));
  el("primeiro-titulo").addEventListener("click", () => resetForm(true));
  el("cancelar-edicao").addEventListener("click", () => { resetForm(); el("colecao").focus(); });
  el("tentar-novamente").addEventListener("click", load);
  syncSeasons();
  load();
})();
