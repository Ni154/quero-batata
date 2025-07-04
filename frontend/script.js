const apiUrl = "https://SEU_BACKEND_URL/api/pedido";

const produtos = [
  { nome: "Batata Cheddar Bacon", preco: 25 },
  { nome: "Batata Calabresa Catupiry", preco: 28 },
];

let carrinho = [];

function renderProdutos() {
  const div = document.getElementById("produtos");
  div.innerHTML = produtos
    .map((p, i) => `<div>
        ${p.nome} - R$ ${p.preco.toFixed(2)}
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
  div.innerHTML = "<h2>Carrinho:</h2>" + carrinho
    .map((item) => `<div>${item.nome} - R$ ${item.preco.toFixed(2)}</div>`)
    .join("");
}

function finalizarPedido() {
  const nome = prompt("Digite seu nome:");
  const endereco = prompt("Digite seu endereço:");
  const telefone = prompt("Digite seu telefone:");
  const taxa_entrega = 5.00;

  const total = carrinho.reduce((soma, item) => soma + item.preco, 0) + taxa_entrega;

  fetch(apiUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      nome,
      endereco,
      telefone,
      produtos: carrinho,
      taxa_entrega,
      total
    }),
  })
    .then((res) => res.json())
    .then((res) => {
      alert("Pedido enviado com sucesso!");
      if (res.pdf_url) window.open(res.pdf_url, "_blank");
    });
}

renderProdutos();

