const API = "/api";
const token = localStorage.getItem('token');
if(!token){ location.href = '/'; }

function hdr(){ return { 'Authorization': `Bearer ${token}` }; }

document.getElementById('logout').onclick = ()=>{ localStorage.removeItem('token'); location.href='/'; };

async function whoami(){
  const res = await fetch(`${API}/me`, { headers: hdr() });
  if(res.ok){ const me = await res.json(); document.getElementById('me').textContent = me.name; }
}

async function list(q=""){ const res = await fetch(`${API}/projects${q?`?q=${encodeURIComponent(q)}`:''}`, { headers: hdr() }); return res.json(); }

function render(list){
  const root = document.getElementById('projects');
  root.innerHTML = '';
  for(const p of list){
    const card = document.createElement('div');
    card.className = 'project-card';
    card.innerHTML = `<div style="font-weight:700; margin-bottom:6px;">${p.name}</div><div class="small">${p.description||''}</div>`;
    card.onclick = ()=> location.href = `/board.html?project=${p.id}&name=${encodeURIComponent(p.name)}`;
    root.appendChild(card);
  }
}

async function bootstrap(){
  await whoami();
  render(await list());
  const search = document.getElementById('search');
  search.addEventListener('input', async ()=>{ render(await list(search.value)); });
  document.getElementById('create').onclick = async ()=>{
    const name = document.getElementById('new-name').value.trim();
    if(!name) return;
    const res = await fetch(`${API}/projects`, { method:'POST', headers: { ...hdr(), 'Content-Type':'application/json' }, body: JSON.stringify({name}) });
    if(res.ok){
      document.getElementById('new-name').value='';
      render(await list(document.getElementById('search').value));
    } else {
      alert('Could not create project');
    }
  };
}

bootstrap();
