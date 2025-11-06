const API = "/api";
const loginForm = document.getElementById("login");
const signupForm = document.getElementById("signup");
const tabLogin = document.getElementById("tab-login");
const tabSignup = document.getElementById("tab-signup");

function setTab(which){
  if(which==='login'){ loginForm.style.display='flex'; signupForm.style.display='none'; tabLogin.classList.add('primary'); tabSignup.classList.remove('primary'); }
  else { signupForm.style.display='flex'; loginForm.style.display='none'; tabSignup.classList.add('primary'); tabLogin.classList.remove('primary'); }
}

tabLogin.onclick=()=>setTab('login');
tabSignup.onclick=()=>setTab('signup');

loginForm.onsubmit = async (e)=>{
  e.preventDefault();
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;
  const body = new URLSearchParams();
  body.append('username', email);
  body.append('password', password);
  try {
    const res = await fetch(`${API}/auth/login`, { method:'POST', body });
    if(!res.ok) throw new Error('Login failed');
    const data = await res.json();
    localStorage.setItem('token', data.access_token);
    location.href = '/projects.html';
  } catch(err){ alert(err.message); }
}

signupForm.onsubmit = async (e)=>{
  e.preventDefault();
  const payload = {
    name: document.getElementById('signup-name').value,
    email: document.getElementById('signup-email').value,
    password: document.getElementById('signup-password').value,
  };
  try {
    const res = await fetch(`${API}/auth/signup`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
    if(!res.ok) throw new Error('Signup failed');
    const loginRes = await fetch(`${API}/auth/login`, { method:'POST', body: new URLSearchParams({username: payload.email, password: payload.password}) });
    const data = await loginRes.json();
    localStorage.setItem('token', data.access_token);
    location.href = '/projects.html';
  } catch(err){ alert(err.message); }
}
