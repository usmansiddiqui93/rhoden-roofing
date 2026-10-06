// Form: Netlify handles it natively; elsewhere show a friendly confirmation
const form=document.getElementById('estimateForm');
form.addEventListener('submit',async e=>{
  e.preventDefault();
  const data=new URLSearchParams(new FormData(form)).toString();
  let ok=false;
  try{const r=await fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:data});ok=r.ok}catch(_){}
  form.innerHTML=ok
   ?'<div class="form-ok">Thanks! Your estimate request is in. A Rhoden Roofing team member will contact you shortly.</div>'
   :'<div class="form-ok">Thanks! This is a staging site, so the form isn’t connected yet. Please call (316) 927-2233 to schedule your free estimate.</div>';
});

