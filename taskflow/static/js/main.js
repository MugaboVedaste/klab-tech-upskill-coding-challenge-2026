document.addEventListener('DOMContentLoaded', function() {
  // Focus first input on forms
  var firstInput = document.querySelector('form input:not([type=hidden])');
  if (firstInput) firstInput.focus();

  // Simple form submit UX: disable submit buttons to prevent double submit
  document.querySelectorAll('form').forEach(function(form){
    form.addEventListener('submit', function(e){
      var btn = form.querySelector('button[type=submit], input[type=submit]');
      if (btn) {
        btn.disabled = true;
        btn.classList.add('btn');
        btn.textContent = btn.getAttribute('data-loading') || 'Please wait...';
      }
    });
  });

  // Enhance any elements with data-confirm attribute
  document.querySelectorAll('[data-confirm]').forEach(function(el){
    el.addEventListener('click', function(e){
      var msg = el.getAttribute('data-confirm') || 'Are you sure?';
      if (!confirm(msg)) e.preventDefault();
    });
  });
});

// small helper to show toast messages (very lightweight)
window.showToast = function(text, timeout){
  timeout = timeout || 3000;
  var t = document.createElement('div');
  t.textContent = text;
  t.style.position = 'fixed';
  t.style.right = '12px';
  t.style.bottom = '12px';
  t.style.background = '#fff';
  t.style.color = '#222';
  t.style.border = '1px solid rgba(0,0,0,0.06)';
  t.style.padding = '8px 12px';
  t.style.borderRadius = '6px';
  t.style.boxShadow = '0 6px 18px rgba(0,0,0,0.04)';
  document.body.appendChild(t);
  setTimeout(function(){ t.remove(); }, timeout);
};
