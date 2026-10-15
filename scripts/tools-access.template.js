/* Acesso às ferramentas do livro Gestão Pastoral, sem servidor próprio.
   A tela original (feita para o servidor do Manus) pergunta duas coisas a /api/trpc/leads.*;
   este arquivo responde a elas aqui mesmo, no navegador do leitor.
   - Código do livro: guarda só a impressão digital (SHA-256), nunca o código em texto aberto.
   - Cadastro de visitante: só é enviado ao Brevo (lista "Livros - ferramentas", dupla confirmação) se a pessoa
     marcar que aceita receber novidades. Sem esse aceite, o e-mail e o nome não saem do navegador.
   Gerado por scripts/build_public.py (não editar o arquivo em public/). */
(function () {
  var CODE_HASH = "__CODE_HASH__";
  var BREVO_URL = "__BREVO_URL__";
  var challenges = {};
  var realFetch = window.fetch.bind(window);

  function sha256hex(s) {
    return crypto.subtle.digest("SHA-256", new TextEncoder().encode(s)).then(function (b) {
      return Array.prototype.map.call(new Uint8Array(b), function (x) { return x.toString(16).padStart(2, "0"); }).join("");
    });
  }
  function ok(data) { return { result: { data: { json: data } } }; }
  function err(message, code, http) {
    return { error: { json: { message: message, code: -32600, data: { code: code, httpStatus: http } } } };
  }

  var handlers = {
    humanChallenge: function () {
      var a = 2 + Math.floor(Math.random() * 8), b = 2 + Math.floor(Math.random() * 8);
      var id = Math.random().toString(36).slice(2);
      challenges[id] = String(a + b);
      return Promise.resolve(ok({ id: id, question: "Quanto é " + a + " + " + b + "?" }));
    },
    verifyBuyerAccess: function (inp) {
      var c = String((inp && inp.code) || "").toUpperCase().replace(/\s+/g, "");
      if (!c) return Promise.resolve(err("Código inválido", "UNAUTHORIZED", 401));
      return sha256hex(c).then(function (h) {
        return h === CODE_HASH ? ok({ success: true }) : err("Código inválido", "UNAUTHORIZED", 401);
      });
    },
    subscribe: function (inp) {
      inp = inp || {};
      if (inp.website) return Promise.resolve(ok({ success: true })); // campo escondido: robô
      var expected = challenges[inp.challengeId];
      delete challenges[inp.challengeId];
      if (!expected || String(inp.challengeAnswer || "").trim() !== expected)
        return Promise.resolve(err("Resposta incorreta. Tente de novo com a nova conta.", "BAD_REQUEST", 400));
      if (String(inp.name || "").trim().length < 2)
        return Promise.resolve(err("Informe seu nome.", "BAD_REQUEST", 400));
      var email = String(inp.email || "").trim();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
        return Promise.resolve(err("Confira o e-mail digitado.", "BAD_REQUEST", 400));
      if (inp.consent === true) {
        var body = new URLSearchParams({ EMAIL: email, OPT_IN: "1", email_address_check: "", locale: "pt" });
        realFetch(BREVO_URL, { method: "POST", mode: "no-cors", body: body }).catch(function () {});
      }
      return Promise.resolve(ok({ success: true }));
    }
  };

  function readBody(input, init) {
    if (init && typeof init.body === "string") return Promise.resolve(init.body);
    if (input && typeof input !== "string" && input.text) return input.text();
    return Promise.resolve("");
  }

  function handle(urlStr, input, init) {
    var u = new URL(urlStr, location.href);
    var names = decodeURIComponent(u.pathname.split("/api/trpc/")[1] || "").split(",");
    var method = ((init && init.method) || (input && input.method) || "GET").toUpperCase();
    var getInputs = method === "GET"
      ? Promise.resolve(u.searchParams.get("input"))
      : readBody(input, init);
    return getInputs.then(function (raw) {
      var inputs = {};
      try { inputs = raw ? JSON.parse(raw) : {}; } catch (e) {}
      return Promise.all(names.map(function (n, i) {
        var h = handlers[n.replace(/^leads\./, "")];
        var data = inputs && inputs[i] ? inputs[i].json : undefined;
        return h ? h(data) : Promise.resolve(err("Procedimento não encontrado: " + n, "NOT_FOUND", 404));
      }));
    }).then(function (results) {
      return new Response(JSON.stringify(results), { status: 200, headers: { "content-type": "application/json" } });
    });
  }

  window.fetch = function (input, init) {
    var url = typeof input === "string" ? input : (input && input.url) || String(input);
    if (url.indexOf("/api/trpc/") > -1) return handle(url, input, init);
    return realFetch(input, init);
  };
})();
