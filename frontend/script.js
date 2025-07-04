const API_BASE_URL = "https://quero-batata-production.up.railway.app";

async function carregarCardapio() {
  const categoriasRes = await fetch(`${API_BASE_URL}/api/categorias`);
  const categorias = await categoriasRes.json();

  const produtosRes = await fetch(`${API_BASE_URL}/api/produtos`);
  const produtos = await produtosRes.json();

  const divCategorias = document.querySelector('.categorias');
  const divProdutos = document.getElementById('produtos');

  // Limpar
  divCategorias.innerHTML = '';
  divProdutos.innerHTML = '';

  categorias.forEach(cat => {
    const catDiv = document.createElement('div');
    catDiv.className = 'categoria';
    catDiv.textContent = cat.nome;
    catDiv.onclick = () => mostrarCategoria(cat.id, produtos);
    divCategorias.appendChild(catDiv);
  });

  // Mostrar produtos da primeira categoria por padrão
  if (categorias.length > 0) {
    mostrarCategoria(categorias[0].id, produtos);
  }
}

function mostrarCategoria(catId, produtos) {
  // Marcar categoria ativa
  document.querySelectorAll('.categoria').forEach(el => el.classList.remove('ativa'));
  event.target.classList.add('ativa');

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

// Chama ao carregar a página
window.onload = carregarCardapio;
