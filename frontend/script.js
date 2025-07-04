<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <title>Quero Batata - Pedido Online</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; max-width: 480px; margin: auto; }
    #produtos > div { margin-bottom: 8px; }
    #carrinho > div { margin-bottom: 6px; }
    #formulario-pedido { 
      display: none; 
      border: 1px solid #ccc; 
      padding: 15px; 
      margin-top: 20px; 
      border-radius: 6px; 
      background: #f9f9f9;
    }
    label { display: block; margin-bottom: 8px; }
    input[type="text"] { width: 100%; padding: 6px; box-sizing: border-box; }
    button { margin-right: 10px; padding: 8px 15px; cursor: pointer; }
  </style>
</head>
<body>

  <h1>Quero Batata - Cardápio</h1>

  <div id="produtos"></div>

  <div id="carrinho"></div>

  <button onclick="finalizarPedido()">Finalizar Pedido</button>

  <div id="formulario-pedido">
    <h3>Finalize seu Pedido</h3>
    <label>Nome:
      <input type="text" id="nomeCliente" />
    </label>
    <label>Endereço:
      <input type="text" id="enderecoCliente" />
    </label>
    <label>Telefone:
      <input type="text" id="telefoneCliente" />
    </label>
    <button onclick="enviarPedido()">Enviar Pedido</button>
    <button onclick="cancelarPedido()">Cancelar</button>
  </div>

<script>
  const apiUrl = "https://quero-batata-production.up.railway.app/api/pedido"; // Altere para sua API real

  const produtos = [
    { nome: "Batata Cheddar Bacon", preco: 25 },
    { nome: "Batata Calabresa Catupiry", preco: 28 },
    // pode adicionar mais produtos aqui
  ];

  let carrinho = [];

  function renderProdutos() {
    const div = document.getElementById("produtos");
    div.innerHTML = produtos
      .map((p, i) => `<div>
          <strong>${p.nome}</strong> - R$ ${p.preco.toFixed(2)}
          <button onclick="adicionar(${i})">Adicionar</button>
        </div>`)
      .join("");
  }

  function adicionar(i) {
    carrinho.push(produtos[i]);
    renderCarrinho();
  }

  function renderCarrinho() {
    const div = document.getElementById("carrinho");
    if (carrinho.length === 0) {
      div.innerHTML = "<p>Carrinho vazio.</p>";
      return;
    }
    const total = carrinho.reduce((sum, item) => sum + item.preco, 0);
    div.innerHTML = "<h2>Carrinho:</h2>" + 
      carrinho.map(item => `<div>${item.nome} - R$ ${item.preco.toFixed(2)}</div>`).join("") +
      `<hr><b>Total: R$ ${total.toFixed(2)}</b>`;
  }

  function finalizarPedido() {
    if (carrinho.length === 0) {
      alert("Seu carrinho está vazio!");
      return;
    }
    document.getElementById("formulario-pedido").style.display = "block";
  }

  function cancelarPedido() {
    document.getElementById("formulario-pedido").style.display = "none";
  }

  function enviarPedido() {
    const nome = document.getElementById("nomeCliente").value.trim();
    const endereco = document.getElementById("enderecoCliente").value.trim();
    const telefone = document.getElementById("telefoneCliente").value.trim();
    const taxa_entrega = 5.0;

    if (!nome || !endereco || !telefone) {
      alert("Preencha todos os campos.");
      return;
    }

    const total = carrinho.reduce((sum, item) => sum + item.preco, 0) + taxa_entrega;

    // Caso tenha token de login salvo no localStorage, pode ser enviado aqui:
    const token = localStorage.getItem("token");

    fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({
        nome,
        endereco,
        telefone,
        produtos: carrinho,
        taxa_entrega,
        total,
      }),
    })
      .then(res => {
        if (!res.ok) {
          return res.json().then(err => { throw new Error(err.erro || 'Erro ao enviar pedido') });
        }
        return res.json();
      })
      .then(res => {
        alert("Pedido enviado com sucesso!");
        if (res.pdf_url) window.open(res.pdf_url, "_blank");
        carrinho = [];
        renderCarrinho();
        cancelarPedido();
        // limpa inputs
        document.getElementById("nomeCliente").value = "";
        document.getElementById("enderecoCliente").value = "";
        document.getElementById("telefoneCliente").value = "";
      })
      .catch(err => alert("Erro: " + err.message));
  }

  // Inicializa a lista
  renderProdutos();
  renderCarrinho();
</script>

</body>
</html>
