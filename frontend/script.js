const API_BASE_URL = "https://quero-batata-production.up.railway.app";

let carrinho = [];

async function carregarCardapio() {
  const categoriasRes = await fetch(`${API_BASE_URL}/api/categorias`);
  const categorias = await categoriasRes.json();

  const produtosRes = await fetch(`${API_BASE_URL}/api/produtos`);
  const produtos = await produtosRes.json();

  const divCategorias = document.querySelector('.categorias');
  const divProdutos = document.getElementById('produtos');

  // Limpar áreas
  divCategorias.innerHTML = '';
  divProdutos.innerHTML = '';

  categorias.forEach(cat => {
    const catDiv = document.createElement('div');
    catDiv.className = 'categoria';
    catDiv.textContent = cat.nome;
    catDiv.onclick = (event) => mostrarCategoria(cat.id, produtos, event);
    divCategorias.appendChild(catDiv);
  });

  // Mostrar produtos da primeira categoria por padrão
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
    const card = document.createElement("div");
    card.className = "card";
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

function abrirModalPedido() {
  if (carrinho.length === 0) {
    alert("Adicione itens ao carrinho.");
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

function enviarPedido() {
  const nome = document.getElementById("nome").value.trim();
  const telefone = document.getElementById("telefone").value.trim();
  const endereco = document.getElementById("endereco").value.trim();

  if (!nome || !telefone || !endereco) {
    alert("Preencha todos os campos!");
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
      total
    })
  })
  .then(res => {
    if(!res.ok) throw new Error("Erro ao enviar pedido");
    return res.json();
  })
  .then(data => {
    alert("Pedido enviado com sucesso!");
    carrinho = [];
    atualizarCarrinho();
    fecharModalPedido();

    // Pode usar esse evento para notificação no painel, se implementado
    const event = new CustomEvent('novoPedido', { detail: data });
    window.dispatchEvent(event);
  })
  .catch(err => {
    console.error(err);
    alert("Erro ao enviar pedido.");
  });
}

// Chama o carregamento do cardápio ao carregar a página
window.onload = carregarCardapio;
