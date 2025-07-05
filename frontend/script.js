const API_BASE_URL = "https://quero-batata-production.up.railway.app";

let carrinho = [];

async function carregarCardapio() {
  const categoriasRes = await fetch(`${API_BASE_URL}/api/categorias`);
  const categorias = await categoriasRes.json();

  const produtosRes = await fetch(`${API_BASE_URL}/api/produtos`);
  const produtos = await produtosRes.json();

  const divCategorias = document.querySelector('.categorias');
  const divProdutos = document.getElementById('produtos');

  divCategorias.innerHTML = '';
  divProdutos.innerHTML = '';

  categorias.forEach(cat => {
    const catDiv = document.createElement('div');
    catDiv.className = 'categoria';
    catDiv.textContent = cat.nome;
    catDiv.onclick = (event) => mostrarCategoria(cat.id, produtos, event);
    divCategorias.appendChild(catDiv);
  });

  if (categorias.length > 0) {
    mostrarCategoria(categorias[0].id, produtos);
  }
}

function mostrarCategoria(catId, produtos, event) {
  document.querySelectorAll('.categoria').forEach(el => el.classList.remove('ativa'));
  if (event) event.target.classList.add('ativa');

  const div = document.getElementById('produtos');
  div.innerHTML = `<div class="secao"><h2>Batatas com Categoria ${catId}</h2></div>`;

  produtos.filter(p => p.categoria_id === catId).forEach(p => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <img src="${p.img_url || 'https://via.placeholder.com/100x80'}" alt="${p.nome}" />
      <div class="card-info">
        <h3>${p.nome}</h3>
        <p>${p.descricao || ''}</p>
        <div class="preco">R$ ${p.preco.toFixed(2)}</div>
        <button onclick="adicionarCarrinho('${p.nome}', ${p.preco})">Adicionar</button>
      </div>`;
    div.appendChild(card);
  });
}

function adicionarCarrinho(nome, preco) {
  const existente = carrinho.find(item => item.nome === nome);
  if (existente) {
    existente.qtd++;
  } else {
    carrinho.push({ nome, preco, qtd: 1 });
  }
  atualizarCarrinho();
}

function atualizarCarrinho() {
  const div = document.getElementById("carrinho-itens");
  if (carrinho.length === 0) {
    div.innerHTML = "Seu carrinho está vazio.";
    document.getElementById("total").innerText = "0,00";
    return;
  }
  let html = "<ul>", total = 0;
  carrinho.forEach(item => {
    html += `<li>${item.nome} x ${item.qtd} = R$ ${(item.qtd * item.preco).toFixed(2)}</li>`;
    total += item.qtd * item.preco;
  });
  html += "</ul>";
  div.innerHTML = html;
  document.getElementById("total").innerText = total.toFixed(2);
}

async function verificarStatusLoja() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/status`);
    if (!res.ok) throw new Error('Erro ao consultar status da loja');
    const data = await res.json();
    return data.loja_aberta;
  } catch (error) {
    console.error("Erro ao verificar status da loja:", error);
    return false;
  }
}

async function abrirModalPedido() {
  const lojaAberta = await verificarStatusLoja();
  if (!lojaAberta) {
    alert("No momento, a loja está fechada. Não é possível fazer pedidos.");
    return;
  }
  if (carrinho.length === 0) {
    alert("Adicione itens ao carrinho antes de finalizar o pedido.");
    return;
  }
  const taxa_entrega = 5.00;
  const subtotal = carrinho.reduce((s, i) => s + i.qtd * i.preco, 0);
  const total = subtotal + taxa_entrega;
  document.getElementById("modalTotal").innerText = total.toFixed(2);
  document.getElementById("modalPedido").style.display = "flex";
}

function fecharModalPedido() {
  document.getElementById("modalPedido").style.display = "none";
}

async function enviarPedido() {
  const lojaAberta = await verificarStatusLoja();
  if (!lojaAberta) {
    alert("A loja fechou antes de concluir seu pedido. Tente novamente mais tarde.");
    fecharModalPedido();
    return;
  }

  const nome = document.getElementById("nome").value.trim();
  const telefone = document.getElementById("telefone").value.trim();
  const endereco = document.getElementById("endereco").value.trim();
  const formaPagamento = document.getElementById("formaPagamento").value;

  if (!nome || !telefone || !endereco) {
    alert("Por favor, preencha todos os campos.");
    return;
  }

  if (!formaPagamento) {
    alert("Por favor, selecione a forma de pagamento.");
    return;
  }

  const taxa_entrega = 5.00;
  const subtotal = carrinho.reduce((s, i) => s + i.qtd * i.preco, 0);
  const total = subtotal + taxa_entrega;

  fetch(`${API_BASE_URL}/api/pedido`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      nome,
      telefone,
      endereco,
      produtos: carrinho,
      taxa_entrega,
      total,
      forma_pagamento: formaPagamento
    })
  })
    .then(res => {
      if (!res.ok) throw new Error("Erro ao enviar pedido");
      return res.json();
    })
    .then(() => {
      alert("Pedido enviado com sucesso!");
      carrinho = [];
      atualizarCarrinho();
      fecharModalPedido();
    })
    .catch(err => {
      console.error(err);
      alert("Erro ao enviar pedido.");
    });
}

window.onload = carregarCardapio;
