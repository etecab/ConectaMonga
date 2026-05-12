// =============================================
//  ConectaMonga — app.js
//  Lógica principal do frontend
// =============================================

// ── URL DO BACKEND ──
const API = "https://fearless-fulfillment-production-7d7e.up.railway.app";

// ── DADOS DE EXEMPLO ──
const sampleEvents = [
  {
    id: 1, title: 'Festival de Verão Mongaguá 2025', category: 'Show',
    date: '2025-01-18', time: '20:00',
    local: 'Avenida Beira Mar, 500 – Mongaguá',
    wpp: '(13) 99811-2233',
    desc: 'O maior festival de verão do litoral paulista! Com bandas ao vivo, gastronomia local e muito mais.',
    company: 'Balneário Music', companyInit: 'BM', segment: 'Entretenimento',
    likes: 84, img: 'https://images.unsplash.com/photo-1506157786151-b8491531f063?w=600&q=80'
  },
  {
    id: 2, title: 'Noite de Samba & Pagode', category: 'Festa',
    date: '2025-01-25', time: '21:00',
    local: 'Rua São Paulo, 120 – Centro',
    wpp: '(13) 99711-5522',
    desc: 'Uma noite de muito samba ao som dos melhores grupos da região.',
    company: 'Bar do Caju', companyInit: 'BC', segment: 'Gastronomia',
    likes: 52, img: 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=600&q=80'
  },
  {
    id: 3, title: 'Torneio de Beach Tennis', category: 'Esporte',
    date: '2025-02-01', time: '08:00',
    local: 'Praia de Mongaguá – Sector 3',
    wpp: '(13) 99999-0001',
    desc: 'Venha participar do torneio amador de beach tennis! Inscrições abertas para duplas mistas.',
    company: 'Sport Litoral', companyInit: 'SL', segment: 'Esportes',
    likes: 37, img: 'https://images.unsplash.com/photo-1554284126-aa88f22d8b74?w=600&q=80'
  },
  {
    id: 4, title: 'Feira Gastronômica da Primavera', category: 'Gastronomia',
    date: '2025-02-08', time: '12:00',
    local: 'Praça Central – Mongaguá',
    wpp: '(13) 99800-3344',
    desc: 'Sabores do litoral em um só lugar. Frutos do mar, petiscos e doces artesanais.',
    company: 'Sabores do Mar', companyInit: 'SM', segment: 'Gastronomia',
    likes: 61, img: 'https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=600&q=80'
  },
  {
    id: 5, title: 'Espetáculo de Teatro na Praia', category: 'Cultural',
    date: '2025-02-14', time: '19:30',
    local: 'Concha Acústica Municipal',
    wpp: '(13) 99655-1122',
    desc: 'Um espetáculo ao ar livre para toda a família, com entrada gratuita.',
    company: 'Arte & Praia', companyInit: 'AP', segment: 'Cultura',
    likes: 29, img: 'https://images.unsplash.com/photo-1503095396549-807759245b35?w=600&q=80'
  },
  {
    id: 6, title: 'Réveillon na Beira Mar 2026', category: 'Festa',
    date: '2025-12-31', time: '22:00',
    local: 'Praia Central – Mongaguá',
    wpp: '(13) 99911-4400',
    desc: 'Queima de fogos, shows ao vivo e muita energia para celebrar o novo ano!',
    company: 'Evento Litoral', companyInit: 'EL', segment: 'Entretenimento',
    likes: 198, img: 'https://images.unsplash.com/photo-1467810563316-b5af2cc7f37b?w=600&q=80'
  }
];

const sampleCompanies = [
  { name: 'Balneário Music', init: 'BM', segment: 'Entretenimento', city: 'Mongaguá', events: 4 },
  { name: 'Bar do Caju', init: 'BC', segment: 'Gastronomia', city: 'Mongaguá', events: 2 },
  { name: 'Sport Litoral', init: 'SL', segment: 'Esportes', city: 'Mongaguá', events: 3 },
  { name: 'Sabores do Mar', init: 'SM', segment: 'Gastronomia', city: 'Mongaguá', events: 5 },
  { name: 'Arte & Praia', init: 'AP', segment: 'Cultura', city: 'Mongaguá', events: 1 },
  { name: 'Evento Litoral', init: 'EL', segment: 'Entretenimento', city: 'Mongaguá', events: 6 }
];

// ── ESTADO ──
let currentUser = null;
let likedEvents  = new Set();
let currentFilter = 'todos';
let activeEventId = null;
let comments = { 1:[], 2:[], 3:[], 4:[], 5:[], 6:[] };
let events = [...sampleEvents];

// =============================================
//  RENDERIZAÇÃO
// =============================================

function renderEvents(list) {
  const grid = document.getElementById('eventsGrid');
  if (!list.length) {
    grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1">
      <i class="fas fa-calendar-times"></i>
      <h3>Nenhum evento encontrado</h3>
      <p>Tente outra busca ou categoria.</p>
    </div>`;
    return;
  }
  document.getElementById('event-count').textContent =
    `Mostrando ${list.length} evento${list.length !== 1 ? 's' : ''}`;

  grid.innerHTML = list.map(e => `
    <div class="event-card" onclick="openEventDetail(${e.id})">
      ${e.img
        ? `<img class="event-img" src="${e.img}" alt="${e.title}"
              onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
           <div class="event-img-placeholder" style="display:none"><i class="fas fa-calendar-star"></i></div>`
        : `<div class="event-img-placeholder"><i class="fas fa-calendar-star"></i></div>`
      }
      <div class="event-body">
        <span class="event-category">${e.category}</span>
        <div class="event-title">${e.title}</div>
        <div class="event-meta">
          <span><i class="fas fa-calendar"></i>${formatDate(e.date)}</span>
          <span><i class="fas fa-clock"></i>${e.time}</span>
          <span><i class="fas fa-map-marker-alt"></i>${e.local}</span>
        </div>
        <div class="event-footer">
          <a class="event-company" onclick="event.stopPropagation()">
            <div class="company-avatar">${e.companyInit}</div>
            <span>${e.company}</span>
          </a>
          <button class="like-btn ${likedEvents.has(e.id) ? 'liked' : ''}"
            onclick="event.stopPropagation(); toggleLike(${e.id}, this)">
            <i class="${likedEvents.has(e.id) ? 'fas' : 'far'} fa-heart"></i> ${e.likes}
          </button>
        </div>
      </div>
    </div>
  `).join('');
}

function renderCompanies() {
  const grid = document.getElementById('companiesGrid');
  grid.innerHTML = sampleCompanies.map(c => `
    <div class="event-card" style="cursor:default;">
      <div class="event-img-placeholder" style="height:120px;">
        <span style="font-family:'Sora';font-size:2rem;font-weight:700;color:rgba(255,255,255,0.8);">${c.init}</span>
      </div>
      <div class="event-body">
        <span class="event-category">${c.segment}</span>
        <div class="event-title">${c.name}</div>
        <div class="event-meta">
          <span><i class="fas fa-map-marker-alt"></i>${c.city}, SP</span>
          <span><i class="fas fa-calendar-check"></i>${c.events} eventos publicados</span>
        </div>
        <div class="event-footer">
          <button class="btn btn-solid" style="font-size:0.8rem;padding:6px 14px;"
            onclick="showToast('Perfil em breve!')">Ver perfil</button>
          <button class="like-btn" onclick="showToast('Seguindo ${c.name}!')">
            <i class="far fa-bookmark"></i> Seguir
          </button>
        </div>
      </div>
    </div>
  `).join('');
}

// =============================================
//  FILTROS
// =============================================

function filterEvents() {
  const q = (document.getElementById('searchInput').value || '').toLowerCase();
  const list = events.filter(e => {
    const matchQ = !q ||
      e.title.toLowerCase().includes(q) ||
      e.company.toLowerCase().includes(q) ||
      e.category.toLowerCase().includes(q);
    const matchCat = currentFilter === 'todos' || e.category.toLowerCase().includes(currentFilter);
    return matchQ && matchCat;
  });
  renderEvents(list);
}

function filterByCategory(cat, el) {
  currentFilter = cat;
  document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
  el.classList.add('active');
  filterEvents();
}

function switchTab(el) {
  document.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  filterEvents();
}

// =============================================
//  DETALHE DO EVENTO
// =============================================

function openEventDetail(id) {
  const e = events.find(x => x.id === id);
  if (!e) return;
  activeEventId = id;

  document.getElementById('detailTitle').textContent    = e.title;
  document.getElementById('detailCategory').textContent = e.category;
  document.getElementById('detailDate').textContent     = formatDate(e.date);
  document.getElementById('detailTime').textContent     = e.time;
  document.getElementById('detailLocal').textContent    = e.local;
  document.getElementById('detailWpp').textContent      = e.wpp;
  document.getElementById('detailDesc').textContent     = e.desc;
  document.getElementById('detailCompanyName').textContent = e.company;
  document.getElementById('detailCompanyAvatar').textContent = e.companyInit;
  document.getElementById('detailCompanySeg').textContent  = e.segment;
  document.getElementById('detailMapAddr').textContent  = e.local;

  const imgC = document.getElementById('detailImgContainer');
  if (e.img) {
    imgC.innerHTML = `<img src="${e.img}" style="width:100%;height:240px;object-fit:cover;"
      onerror="this.parentElement.innerHTML='<i class=\\'fas fa-calendar-star\\'></i>'">`;
  } else {
    imgC.innerHTML = `<i class="fas fa-calendar-star"></i>`;
  }

  document.querySelectorAll('.star').forEach(s => s.classList.remove('lit'));
  renderComments(id);
  openModal('eventDetailModal');
}

// =============================================
//  COMENTÁRIOS
// =============================================

function renderComments(id) {
  const list = comments[id] || [];
  const el = document.getElementById('commentsList');
  if (!list.length) {
    el.innerHTML = `<p style="color:var(--muted);font-size:0.85rem;text-align:center;padding:0.75rem;">
      Seja o primeiro a comentar!</p>`;
    return;
  }
  el.innerHTML = list.map(c => `
    <div class="comment">
      <div class="comment-avatar">${c.init}</div>
      <div class="comment-bubble">
        <div class="comment-name">${c.name}</div>
        <div class="comment-text">${c.text}</div>
        <div class="comment-time">${c.time}</div>
      </div>
    </div>
  `).join('');
}

function addComment() {
  const input = document.getElementById('commentInput');
  const text  = input.value.trim();
  if (!text) return;

  const name = currentUser ? currentUser.name : 'Visitante';
  const init = name.charAt(0).toUpperCase();
  if (!comments[activeEventId]) comments[activeEventId] = [];
  comments[activeEventId].unshift({ name, init, text, time: 'Agora mesmo' });

  renderComments(activeEventId);
  input.value = '';
  showToast('Comentário enviado!');
}

function rateStar(n) {
  document.querySelectorAll('.star').forEach((s, i) => {
    s.classList.toggle('lit', i < n);
  });
  showToast(`Você deu ${n} estrela${n > 1 ? 's' : ''}!`);
}

// =============================================
//  CURTIDAS
// =============================================

function toggleLike(id, btn) {
  const ev = events.find(e => e.id === id);
  if (likedEvents.has(id)) {
    likedEvents.delete(id);
    ev.likes--;
    btn.classList.remove('liked');
    btn.innerHTML = `<i class="far fa-heart"></i> ${ev.likes}`;
  } else {
    likedEvents.add(id);
    ev.likes++;
    btn.classList.add('liked');
    btn.innerHTML = `<i class="fas fa-heart"></i> ${ev.likes}`;
  }
  renderLikedEvents();
}

function renderLikedEvents() {
  const c = document.getElementById('liked-count');
  if (c) c.textContent = likedEvents.size;

  const grid = document.getElementById('liked-events-grid');
  if (!grid) return;

  const liked = events.filter(e => likedEvents.has(e.id));
  if (!liked.length) {
    grid.innerHTML = `<div class="empty-state">
      <i class="fas fa-heart"></i>
      <h3>Nenhum evento curtido</h3>
      <p>Curta eventos para vê-los aqui!</p>
    </div>`;
    return;
  }
  grid.innerHTML = liked.map(e => `
    <div class="event-card" onclick="showPage('home'); setTimeout(()=>openEventDetail(${e.id}),100)">
      <div class="event-img-placeholder" style="height:120px;"><i class="fas fa-calendar-star"></i></div>
      <div class="event-body">
        <span class="event-category">${e.category}</span>
        <div class="event-title">${e.title}</div>
        <div class="event-meta"><span><i class="fas fa-calendar"></i>${formatDate(e.date)}</span></div>
      </div>
    </div>
  `).join('');
}

// =============================================
//  AUTENTICAÇÃO
// =============================================

async function doLogin() {
  const email = document.getElementById('loginEmail').value;
  const pass  = document.getElementById('loginPass').value;
  if (!email || !pass) { showToast('Preencha email e senha!'); return; }

  try {
    // Tenta login como usuário comum
    let res = await fetch(`${API}/api/usuarios/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, senha: pass })
    });

    // Se não encontrou, tenta como empresa
    if (res.status === 401) {
      res = await fetch(`${API}/api/empresas/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, senha: pass })
      });
    }

    const data = await res.json();
    if (!res.ok) { showToast(data.erro || 'Erro ao fazer login'); return; }

    currentUser = data.usuario;
    updateNavForUser();
    closeModal('loginModal');
    showToast(`Bem-vindo(a), ${currentUser.name}!`);
  } catch (e) {
    showToast('Erro de conexão com o servidor!');
  }
}

async function doRegister() {
  const name  = document.getElementById('regName').value;
  const email = document.getElementById('regEmail').value;
  const pass  = document.getElementById('regPass').value;
  if (!name || !email || !pass) { showToast('Preencha todos os campos!'); return; }

  try {
    const res = await fetch(`${API}/api/usuarios/cadastro`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nome: name, email, senha: pass })
    });
    const data = await res.json();
    if (!res.ok) { showToast(data.erro || 'Erro ao cadastrar'); return; }

    currentUser = { name, email, type: 'user', init: name[0].toUpperCase() };
    updateNavForUser();
    closeModal('loginModal');
    showToast(`Conta criada! Bem-vindo(a), ${name}!`);
  } catch (e) {
    showToast('Erro de conexão com o servidor!');
  }
}

async function doEmpresaRegister() {
  const name  = document.getElementById('empName').value;
  const cnpj  = document.getElementById('empCnpj').value;
  const email = document.getElementById('empEmail').value;
  const pass  = document.getElementById('empPass').value;

  if (!name || !cnpj || !email || !pass) {
    showToast('Preencha todos os campos obrigatórios!'); return;
  }
  if (cnpj.replace(/\D/g, '').length < 14) {
    showToast('CNPJ inválido!'); return;
  }

  try {
    const res = await fetch(`${API}/api/empresas/cadastro`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        nome: name, cnpj, email, senha: pass,
        cidadeId: 1, segmentoId: 1,
        telefone: document.getElementById('empTelefone')?.value || ''
      })
    });
    const data = await res.json();
    if (!res.ok) { showToast(data.erro || 'Erro ao cadastrar empresa'); return; }

    currentUser = {
      id: data.id, name, email, type: 'empresa',
      segment: document.getElementById('empSegmento')?.value || 'Entretenimento',
      init: name[0].toUpperCase()
    };

    document.getElementById('dash-company-name').textContent = name;
    document.getElementById('dash-company-seg').textContent  = currentUser.segment;

    updateNavForUser();
    closeModal('loginModal');
    showPage('dashboard');
    showToast(`Empresa ${name} cadastrada com sucesso!`);
  } catch (e) {
    showToast('Erro de conexão com o servidor!');
  }
}

function socialLogin(provider) {
  currentUser = {
    name: `Usuário ${provider}`,
    email: `usuario@${provider.toLowerCase()}.com`,
    type: 'user'
  };
  updateNavForUser();
  closeModal('loginModal');
  showToast(`Conectado via ${provider}!`);
}

function updateNavForUser() {
  const nav  = document.getElementById('nav-actions');
  const init = currentUser.name.charAt(0).toUpperCase();

  nav.innerHTML = `
    <div class="avatar-nav" onclick="toggleDropdown()" style="position:relative;">
      <span>${init}</span>
      <div class="dropdown" id="userDropdown">
        <a href="#" onclick="showPage('profile')"><i class="fas fa-user"></i> Meu Perfil</a>
        ${currentUser.type === 'empresa'
          ? `<a href="#" onclick="showPage('dashboard')"><i class="fas fa-chart-bar"></i> Painel</a>`
          : ''}
        <hr>
        <a href="#" onclick="logout()"><i class="fas fa-sign-out-alt"></i> Sair</a>
      </div>
    </div>
  `;

  if (currentUser.type === 'empresa') {
    document.querySelector('.nav-links').innerHTML = `
      <a href="#" onclick="showPage('home')">Início</a>
      <a href="#" onclick="showPage('dashboard')">Painel</a>
      <a href="#" onclick="showPage('empresas')">Empresas</a>
    `;
  }

  document.getElementById('profile-name-display').textContent  = currentUser.name;
  document.getElementById('profile-email-display').textContent = currentUser.email;
}

function toggleDropdown() {
  const dd = document.getElementById('userDropdown');
  if (dd) dd.classList.toggle('open');
}

function logout() {
  currentUser = null;
  document.getElementById('nav-actions').innerHTML = `
    <a class="btn btn-outline" href="#" onclick="openModal('loginModal')">Entrar</a>
    <a class="btn btn-primary" href="#" onclick="openModal('loginModal'); setTab('register')">Cadastrar</a>
  `;
  document.querySelector('.nav-links').innerHTML = `
    <a href="#" onclick="showPage('home')">Início</a>
    <a href="#" onclick="showPage('home')">Eventos</a>
    <a href="#" onclick="showPage('empresas')">Empresas</a>
    <a href="#" onclick="showPage('home')">Mapa</a>
  `;
  showPage('home');
  showToast('Até logo!');
}

// =============================================
//  PUBLICAR EVENTO
// =============================================

function publishEvent() {
  const title    = document.getElementById('newEvtTitle').value;
  const local    = document.getElementById('newEvtLocal').value;
  const date     = document.getElementById('newEvtDate').value;
  const imgInput = document.getElementById('eventImg');

  if (!title)             { showToast('Adicione um título!'); return; }
  if (!date)              { showToast('Adicione uma data!'); return; }
  if (!local)             { showToast('Adicione o local!'); return; }
  if (!imgInput.files.length) { showToast('A foto de divulgação é obrigatória!'); return; }

  const newId  = events.length + 1;
  const newEvt = {
    id: newId,
    title,
    category: document.getElementById('newEvtCat').value,
    date,
    time:    document.getElementById('newEvtTime').value || '20:00',
    local,
    wpp:     document.getElementById('newEvtWpp').value || '(13) 99999-0000',
    desc:    document.getElementById('newEvtDesc').value || 'Evento incrível em Mongaguá!',
    company:     currentUser ? currentUser.name : 'Empresa',
    companyInit: currentUser ? currentUser.name.charAt(0).toUpperCase() : 'E',
    segment:     currentUser ? currentUser.segment : 'Entretenimento',
    likes: 0, img: null
  };

  const reader = new FileReader();
  reader.onload = function (ev) {
    newEvt.img = ev.target.result;
    events.unshift(newEvt);
    comments[newId] = [];
    renderEvents(events);
    showToast('Evento publicado com sucesso!');

    const sidebarFirst = document.querySelector('.sidebar-nav li a');
    switchDash(sidebarFirst, 'events');

    ['newEvtTitle','newEvtDesc','newEvtDate','newEvtTime','newEvtLocal','newEvtWpp']
      .forEach(id => { document.getElementById(id).value = ''; });
    document.getElementById('imgPreviewContainer').style.display = 'none';
  };
  reader.readAsDataURL(imgInput.files[0]);
}

// =============================================
//  DASHBOARD
// =============================================

function switchDash(el, id) {
  document.querySelectorAll('.sidebar-nav li a').forEach(a => a.classList.remove('active'));
  el.classList.add('active');

  ['overview','events','new-event','profile'].forEach(s => {
    const t = document.getElementById('dash-' + s);
    if (t) t.style.display = 'none';
  });

  const target = document.getElementById('dash-' + id);
  if (target) target.style.display = 'block';

  if (id === 'events') {
    const dg = document.getElementById('dash-events-grid');
    dg.innerHTML = '';
    const myEvents = events.slice(0, 3);
    dg.innerHTML = myEvents.map(e => `
      <div class="event-card" onclick="openEventDetail(${e.id})">
        <div class="event-img-placeholder" style="height:120px;">
          <i class="fas fa-calendar-star"></i>
        </div>
        <div class="event-body">
          <span class="event-category">${e.category}</span>
          <div class="event-title">${e.title}</div>
          <div class="event-meta">
            <span><i class="fas fa-calendar"></i>${formatDate(e.date)}</span>
          </div>
        </div>
      </div>
    `).join('');
  }
}

// =============================================
//  PÁGINAS
// =============================================

function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const target = document.getElementById('page-' + id);
  if (target) target.classList.add('active');
  window.scrollTo(0, 0);

  if (id === 'empresas') renderCompanies();
  if (id === 'profile')  renderLikedEvents();
}

// =============================================
//  MODAIS
// =============================================

function openModal(id)  {
  document.getElementById(id).classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeModal(id) {
  if (id) document.getElementById(id).classList.remove('open');
  else document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('open'));
  document.body.style.overflow = '';
}

function setTab(id) {
  ['login','register','empresa'].forEach(t => {
    document.getElementById('tab-' + t).classList.toggle('active', t === id);
    document.getElementById('panel-' + t).style.display = t === id ? 'block' : 'none';
  });
  const titles = {
    login: 'Acessar sua conta',
    register: 'Criar conta gratuita',
    empresa: 'Cadastrar Empresa'
  };
  document.getElementById('loginModalTitle').textContent = titles[id];
}

// =============================================
//  TOAST
// =============================================

function showToast(msg) {
  const t = document.getElementById('toast');
  document.getElementById('toast-msg').textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}

// =============================================
//  AVATARES
// =============================================

function previewLoginAvatar(input) {
  if (!input.files[0]) return;
  const r = new FileReader();
  r.onload = e => {
    const img = document.getElementById('login-avatar-img');
    img.src = e.target.result;
    img.style.display = 'block';
    const icon = img.parentElement.querySelector('i');
    if (icon) icon.style.display = 'none';
  };
  r.readAsDataURL(input.files[0]);
}

function previewRegAvatar(input)     { previewAvatarById(input, 'reg-avatar-preview'); }
function previewEmpAvatar(input)     { previewAvatarById(input, 'emp-avatar-preview'); }
function previewCompanyAvatar(input) { previewAvatarById(input, 'company-avatar-big'); }

function previewUserAvatar(input) {
  if (!input.files[0]) return;
  const r = new FileReader();
  r.onload = e => {
    const el = document.getElementById('user-avatar-big');
    el.innerHTML = `<img src="${e.target.result}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">`;
  };
  r.readAsDataURL(input.files[0]);
}

function previewAvatarById(input, previewId) {
  if (!input.files[0]) return;
  const r = new FileReader();
  r.onload = ev => {
    const el = document.getElementById(previewId);
    el.innerHTML = `<img src="${ev.target.result}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">`;
  };
  r.readAsDataURL(input.files[0]);
}

function previewEventImg(input) {
  if (!input.files[0]) return;
  const r = new FileReader();
  r.onload = ev => {
    document.getElementById('imgPreview').src = ev.target.result;
    document.getElementById('imgPreviewContainer').style.display = 'block';
  };
  r.readAsDataURL(input.files[0]);
}

// =============================================
//  PERFIL DO USUÁRIO
// =============================================

function saveUserProfile() {
  const name  = document.getElementById('profileName').value;
  const email = document.getElementById('profileEmail').value;
  if (name)  { document.getElementById('profile-name-display').textContent  = name; if (currentUser) currentUser.name  = name; }
  if (email) { document.getElementById('profile-email-display').textContent = email; if (currentUser) currentUser.email = email; }
  showToast('Perfil salvo!');
}

// =============================================
//  UTILITÁRIOS
// =============================================

function formatDate(d) {
  const months = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
  const dt = new Date(d + 'T00:00');
  return `${dt.getDate()} de ${months[dt.getMonth()]} de ${dt.getFullYear()}`;
}

function formatCNPJ(input) {
  let v = input.value.replace(/\D/g, '').substring(0, 14);
  v = v.replace(/^(\d{2})(\d)/, '$1.$2');
  v = v.replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3');
  v = v.replace(/\.(\d{3})(\d)/, '.$1/$2');
  v = v.replace(/(\d{4})(\d)/, '$1-$2');
  input.value = v;
}

// =============================================
//  INICIALIZAÇÃO
// =============================================

async function carregarEventos() {
  try {
    const res = await fetch(`${API}/api/eventos`);
    if (res.ok) {
      const data = await res.json();
      if (data.length > 0) {
        events = data.map(e => ({
          id: e.id,
          title: e.title || e.titulo,
          category: e.category || e.categoria,
          date: e.date || e.data_evento,
          time: e.time || e.horario || '20:00',
          local: e.local,
          wpp: e.wpp || e.contato_whatsapp || '',
          desc: e.desc || e.descricao || '',
          company: e.company || e.empresa,
          companyInit: e.companyInit || (e.company || e.empresa || 'E')[0].toUpperCase(),
          segment: e.segment || e.segmento || '',
          likes: e.likes || 0,
          img: e.img || e.foto_url || null
        }));
      }
    }
  } catch (e) {
    console.warn('Backend offline, usando dados de exemplo.');
  }
  renderEvents(events);
}

document.addEventListener('DOMContentLoaded', () => {
  // Fechar modais ao clicar fora
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', function (e) {
      if (e.target === this) closeModal(this.id);
    });
  });

  // Fechar dropdown ao clicar fora
  document.addEventListener('click', function (e) {
    const dd = document.getElementById('userDropdown');
    if (dd && !dd.parentElement.contains(e.target)) {
      dd.classList.remove('open');
    }
  });

  // Carrega eventos do backend (ou dados de exemplo se offline)
  carregarEventos();
});