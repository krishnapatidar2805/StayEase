// ---------- Navbar mobile toggle ----------
document.addEventListener('DOMContentLoaded', function () {
  const toggle = document.querySelector('.navbar-toggle');
  const links = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', () => links.classList.toggle('open'));
  }

  // ---------- Notification bell dropdown ----------
  const bellBtn = document.getElementById('notifBellBtn');
  const notifDropdown = document.getElementById('notifDropdown');
  if (bellBtn && notifDropdown) {
    bellBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      notifDropdown.classList.toggle('open');
    });
    document.addEventListener('click', (e) => {
      if (!notifDropdown.contains(e.target) && e.target !== bellBtn) {
        notifDropdown.classList.remove('open');
      }
    });
  }

  // ---------- Wishlist AJAX ----------
  document.querySelectorAll('.wishlist-btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const url = this.dataset.url;
      const csrftoken = getCookie('csrftoken');
      fetch(url, {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': csrftoken },
      })
        .then(r => r.json())
        .then(data => {
          const icon = this.querySelector('i');
          if (data.added) {
            icon.classList.remove('bi-heart');
            icon.classList.add('bi-heart-fill');
            this.classList.add('active');
          } else {
            icon.classList.remove('bi-heart-fill');
            icon.classList.add('bi-heart');
            this.classList.remove('active');
          }
        })
        .catch(() => { window.location.href = url; });
    });
  });

  // ---------- Scroll reveal animations ----------
  const revealEls = document.querySelectorAll('[data-aos]');
  if (revealEls.length) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('aos-in');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealEls.forEach(el => observer.observe(el));
  }

  initChatbot();
});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// ---------- AI Chatbot widget ----------
function initChatbot() {
  const toggleBtn = document.getElementById('chat-toggle');
  const chatWindow = document.getElementById('chat-window');
  const closeBtn = document.getElementById('chat-close');
  const form = document.getElementById('chat-form');
  const input = document.getElementById('chat-input');
  const body = document.getElementById('chat-body');

  if (!toggleBtn) return;

  toggleBtn.addEventListener('click', () => {
    chatWindow.classList.toggle('open');
    if (chatWindow.classList.contains('open')) input.focus();
  });
  closeBtn.addEventListener('click', () => chatWindow.classList.remove('open'));

  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
      sendChatMessage(chip.dataset.msg, body, input);
    });
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    const msg = input.value.trim();
    if (!msg) return;
    sendChatMessage(msg, body, input);
  });
}

function appendMessage(body, text, sender) {
  const div = document.createElement('div');
  div.className = `chat-msg ${sender}`;
  div.textContent = text;
  body.appendChild(div);
  body.scrollTop = body.scrollHeight;
}

function sendChatMessage(msg, body, input) {
  appendMessage(body, msg, 'user');
  input.value = '';

  const typing = document.createElement('div');
  typing.className = 'chat-msg bot';
  typing.textContent = 'Typing...';
  body.appendChild(typing);
  body.scrollTop = body.scrollHeight;

  fetch('/chatbot/api/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
    body: JSON.stringify({ message: msg }),
  })
    .then(r => r.json())
    .then(data => {
      typing.remove();
      appendMessage(body, data.response || "Sorry, I didn't get that.", 'bot');
    })
    .catch(() => {
      typing.remove();
      appendMessage(body, 'Connection error. Please try again.', 'bot');
    });
}
