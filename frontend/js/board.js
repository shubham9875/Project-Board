const API = "/api";
const token = localStorage.getItem('token');
if(!token){ location.href = '/'; }
function hdr(){ return { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }; }

document.getElementById('logout').onclick = ()=>{ localStorage.removeItem('token'); location.href='/'; };

const params = new URLSearchParams(location.search);
const projectId = Number(params.get('project'));
const projectName = params.get('name');
document.getElementById('project-title').textContent = projectName || 'Board';

const cols = { todo: document.getElementById('col-todo'), inprogress: document.getElementById('col-inprogress'), done: document.getElementById('col-done') };

function taskEl(task){
  const el = document.createElement('div');
  el.className = 'task';
  el.draggable = true;
  el.dataset.id = task.id;
  el.innerHTML = `<div style="display:flex; justify-content:space-between; align-items:center; gap:8px;">
    <div>${task.title}</div>
    <button data-del="${task.id}">✕</button>
  </div>`;
  el.addEventListener('dragstart', e=>{ el.classList.add('dragging'); e.dataTransfer.setData('text/plain', String(task.id)); });
  el.addEventListener('dragend', ()=> el.classList.remove('dragging'));
  el.querySelector('button').onclick = ()=> delTask(task.id);
  return el;
}

function render(board){
  for(const s of ['todo','inprogress','done']){ cols[s].innerHTML = ''; board[s].forEach((t)=> cols[s].appendChild(taskEl(t))); }
}

async function load(){
  const res = await fetch(`${API}/projects/${projectId}/board`, { headers: { 'Authorization': `Bearer ${token}` } });
  const data = await res.json();
  render(data);
}

async function addTask(){
  const title = document.getElementById('task-title').value.trim();
  if(!title) return;
  const res = await fetch(`${API}/tasks`, { method:'POST', headers: hdr(), body: JSON.stringify({ project_id: projectId, title }) });
  if(res.ok){ document.getElementById('task-title').value=''; load(); }
}

document.getElementById('add-task-btn').onclick = addTask;

// Drag & Drop between columns
for(const column of document.querySelectorAll('.column')){
  column.addEventListener('dragover', e=>{
    e.preventDefault();
    const afterEl = getDragAfterElement(column, e.clientY);
    const draggable = document.querySelector('.dragging');
    const col = column.querySelector('.col');
    if(afterEl == null){ col.appendChild(draggable); } else { col.insertBefore(draggable, afterEl); }
  });
  column.addEventListener('drop', async e=>{
    const status = column.dataset.status;
    await persistOrder(status);
  });
}

function getDragAfterElement(container, y){
  const els = [...container.querySelectorAll('.task:not(.dragging)')];
  return els.reduce((closest, child)=>{
    const box = child.getBoundingClientRect();
    const offset = y - box.top - box.height/2;
    if(offset < 0 && offset > closest.offset){ return { offset, element: child }; } else { return closest; }
  }, { offset: Number.NEGATIVE_INFINITY }).element;
}

async function persistOrder(status){
  for(const s of ['todo','inprogress','done']){
    const col = cols[s];
    [...col.children].forEach(async (el, idx)=>{
      const id = Number(el.dataset.id);
      const payload = { order: idx };
      if(s === status){ payload.status = status; }
      await fetch(`${API}/tasks/${id}`, { method:'PATCH', headers: hdr(), body: JSON.stringify(payload) });
    });
  }
}

async function delTask(id){
  if(!confirm('Delete this task?')) return;
  await fetch(`${API}/tasks/${id}`, { method:'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
  load();
}

load();
