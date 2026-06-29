/* ═══════════════════════════════════════════════════════════
   THE AROMATIC BREEZE – Main JavaScript
═══════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {
  initHeroSwiper();
  initReviewsSwiper();
  initLiveSearch();
  initNewsletterForm();
  initBackToTop();
  initCountdowns();
  initCounterAnimations();
  initCartUpdates();
});

/* ── Hero Swiper ─────────────────────────────────────────── */
function initHeroSwiper() {
  const el = document.querySelector('.hero-swiper');
  if (!el) return;
  new Swiper('.hero-swiper', {
    loop: true,
    autoplay: { delay: 5000, disableOnInteraction: false },
    speed: 800,
    effect: 'fade',
    fadeEffect: { crossFade: true },
    pagination: { el: '.hero-pagination', clickable: true },
    navigation: { nextEl: '.hero-next', prevEl: '.hero-prev' },
  });
}

/* ── Reviews Swiper ──────────────────────────────────────── */
function initReviewsSwiper() {
  const el = document.querySelector('.reviews-swiper');
  if (!el) return;
  new Swiper('.reviews-swiper', {
    slidesPerView: 1,
    spaceBetween: 20,
    loop: true,
    autoplay: { delay: 4000 },
    navigation: { nextEl: '.reviews-next', prevEl: '.reviews-prev' },
    breakpoints: {
      576: { slidesPerView: 2 },
      992: { slidesPerView: 3 },
    }
  });
}

/* ── Live Search ─────────────────────────────────────────── */
function initLiveSearch() {
  const input = document.getElementById('headerSearch');
  const dropdown = document.getElementById('liveSearchResults');
  if (!input || !dropdown) return;

  let timeout;
  input.addEventListener('input', function () {
    clearTimeout(timeout);
    const q = this.value.trim();
    if (q.length < 2) { dropdown.classList.add('d-none'); return; }
    timeout = setTimeout(() => {
      fetch(`${LIVE_SEARCH_URL}?q=${encodeURIComponent(q)}`)
        .then(r => r.json())
        .then(data => {
          if (!data.results.length) { dropdown.classList.add('d-none'); return; }
          dropdown.innerHTML = data.results.map(p => `
            <a href="${p.url}" class="live-search-item">
              ${p.image ? `<img src="${p.image}" alt="${p.name}">` : ''}
              <div>
                <div class="live-search-name">${p.name}</div>
                ${p.inspired_by ? `<div style="font-size:11px;color:#888;">Inspired by: ${p.inspired_by}</div>` : ''}
                <div class="live-search-price">Rs. ${p.price.toLocaleString()}</div>
              </div>
            </a>
          `).join('');
          dropdown.classList.remove('d-none');
        });
    }, 300);
  });

  document.addEventListener('click', function (e) {
    if (!e.target.closest('.search-bar-wrap')) dropdown.classList.add('d-none');
  });
}

/* ── Add to Cart ─────────────────────────────────────────── */
function addToCart(productId, variationId, quantity, btn) {
  const url = `/cart/add/${productId}/`;
  const body = new URLSearchParams({ quantity: quantity || 1 });
  if (variationId) body.append('variation_id', variationId);

  const origText = btn ? btn.innerHTML : '';
  if (btn) { btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Adding...'; btn.disabled = true; }

  fetch(url, {
    method: 'POST',
    headers: {
      'X-CSRFToken': CSRF_TOKEN,
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-Requested-With': 'XMLHttpRequest'
    },
    body: body.toString()
  })
  .then(r => r.json())
  .then(data => {
    if (btn) { btn.innerHTML = '<i class="fas fa-check me-2"></i>Added!'; btn.style.background = '#198754'; }
    // Update cart count
    document.querySelectorAll('.cart-count').forEach(el => el.textContent = data.cart_count);
    showToast(data.message || 'Added to cart!');
    setTimeout(() => {
      if (btn) { btn.innerHTML = origText; btn.disabled = false; btn.style.background = ''; }
    }, 2000);
  })
  .catch(() => { if (btn) { btn.innerHTML = origText; btn.disabled = false; } });
}

/* ── Quick View ──────────────────────────────────────────── */
function openQuickView(slug) {
  const modal = document.getElementById('quickViewModal');
  const content = document.getElementById('quickViewContent');
  if (!modal || !content) return;

  content.innerHTML = '<div class="text-center py-5"><div class="luxury-spinner"></div></div>';
  const bsModal = new bootstrap.Modal(modal);
  bsModal.show();

  fetch(`/product/${slug}/quick-view/`)
    .then(r => r.json())
    .then(p => {
      const mainImg = p.images.find(i => i.is_primary) || p.images[0];
      const imgSrc = mainImg ? mainImg.image : '/static/images/no-product.jpg';
      const price = p.sale_price
        ? `<span style="font-size:1.6rem;font-weight:700;color:#dc3545;">Rs. ${p.sale_price.toLocaleString()}</span>
           <s class="text-muted ms-2">Rs. ${p.regular_price.toLocaleString()}</s>`
        : `<span style="font-size:1.6rem;font-weight:700;">Rs. ${p.selling_price.toLocaleString()}</span>`;

      const thumbs = p.images.map(img =>
        `<img src="${img.image}" alt="" onclick="document.getElementById('qvMainImg').src='${img.image}'"
         style="width:60px;height:60px;object-fit:cover;border-radius:6px;cursor:pointer;border:2px solid #e8e0d0;">`
      ).join('');

      const vars = p.variations.map(v =>
        `<button class="btn-variation" data-vid="${v.id}" data-price="${v.sale_price || v.regular_price}"
         onclick="selectQvVariation(this)" ${!v.stock ? 'disabled class="btn-variation sold-out"' : ''}>
         ${v.name}${!v.stock ? ' (Out)' : ''}
        </button>`
      ).join('');

      content.innerHTML = `
        <div class="row g-0">
          <div class="col-md-5">
            <div style="aspect-ratio:1/1;overflow:hidden;background:#f8f5f0;">
              <img id="qvMainImg" src="${imgSrc}" alt="${p.name}" style="width:100%;height:100%;object-fit:cover;">
            </div>
            <div style="display:flex;gap:6px;padding:10px;flex-wrap:wrap;">${thumbs}</div>
          </div>
          <div class="col-md-7" style="padding:24px;">
            ${p.inspired_by ? `<p style="font-size:12px;color:#888;margin-bottom:4px;">Inspired by: <span style="color:#d4af37;">${p.inspired_by}</span></p>` : ''}
            <h4 style="font-family:'Playfair Display',serif;margin-bottom:12px;">${p.name}</h4>
            <div style="margin-bottom:12px;">${price}</div>
            ${p.short_description ? `<p style="font-size:13px;color:#666;margin-bottom:16px;">${p.short_description}</p>` : ''}
            ${vars ? `<div class="mb-3"><div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">Select Size</div><div style="display:flex;flex-wrap:wrap;gap:6px;">${vars}</div></div>` : ''}
            <div style="display:flex;gap:8px;margin-bottom:16px;">
              <div class="qty-control"><button class="qty-btn" onclick="changeQvQty(-1)">–</button><input id="qvQty" type="number" value="1" min="1" class="qty-input"><button class="qty-btn" onclick="changeQvQty(1)">+</button></div>
            </div>
            <div style="display:flex;gap:8px;margin-bottom:16px;">
              <button class="btn btn-gold flex-grow-1" onclick="addToCart('${p.id}', document.querySelector('.btn-variation.active')?.dataset.vid, document.getElementById('qvQty').value, this)">
                <i class="fas fa-shopping-bag me-2"></i>Add to Cart
              </button>
              <button class="btn btn-outline-gold" onclick="toggleWishlist('${p.id}', this)" title="Wishlist"><i class="far fa-heart"></i></button>
            </div>
            <a href="${p.url}" class="btn btn-outline-secondary w-100" style="font-size:13px;">View Full Details</a>
            <div style="display:flex;gap:10px;margin-top:12px;flex-wrap:wrap;">
              <span style="font-size:11px;color:#888;"><i class="fas fa-award text-warning me-1"></i>Premium Quality</span>
              <span style="font-size:11px;color:#888;"><i class="fas fa-shield-alt text-warning me-1"></i>Secure Payment</span>
              <span style="font-size:11px;color:#888;"><i class="fas fa-undo text-warning me-1"></i>Easy Returns</span>
            </div>
          </div>
        </div>`;
    });
}

function selectQvVariation(btn) {
  document.querySelectorAll('.btn-variation').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}
function changeQvQty(d) {
  const inp = document.getElementById('qvQty');
  if (inp) inp.value = Math.max(1, parseInt(inp.value) + d);
}

/* ── Wishlist Toggle ─────────────────────────────────────── */
function toggleWishlist(productId, btn) {
  fetch(`/accounts/wishlist/toggle/${productId}/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': CSRF_TOKEN, 'X-Requested-With': 'XMLHttpRequest' }
  })
  .then(r => r.json())
  .then(data => {
    const icon = btn.querySelector('i');
    if (data.status === 'added') {
      if (icon) { icon.className = 'fas fa-heart'; }
      btn.classList.add('active');
    } else {
      if (icon) { icon.className = 'far fa-heart'; }
      btn.classList.remove('active');
    }
    document.querySelectorAll('.wishlist-count').forEach(el => el.textContent = data.wishlist_count);
    showToast(data.message);
  })
  .catch(() => {
    showToast('Please login to use wishlist.');
    setTimeout(() => window.location = '/accounts/login/', 1200);
  });
}

/* ── Newsletter ──────────────────────────────────────────── */
function initNewsletterForm() {
  const form = document.getElementById('newsletterForm');
  if (!form) return;
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    const email = form.querySelector('[name=email]').value;
    fetch(NEWSLETTER_URL, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN, 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `email=${encodeURIComponent(email)}`
    })
    .then(r => r.json())
    .then(data => {
      showToast(data.message);
      if (data.status === 'ok') form.reset();
    });
  });
}

/* ── Toast ───────────────────────────────────────────────── */
function showToast(message) {
  const existing = document.querySelector('.luxury-toast');
  if (existing) existing.remove();
  const toast = document.createElement('div');
  toast.className = 'luxury-toast';
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

/* ── Back to Top ─────────────────────────────────────────── */
function initBackToTop() {
  const btn = document.getElementById('backToTop');
  if (!btn) return;
  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 400);
  });
  btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}

/* ── Countdown Timers ────────────────────────────────────── */
function initCountdowns() {
  document.querySelectorAll('[data-end]').forEach(el => {
    const end = new Date(el.dataset.end);
    const tick = () => {
      const diff = end - new Date();
      if (diff <= 0) return;
      const d = Math.floor(diff / 86400000);
      const h = Math.floor((diff % 86400000) / 3600000);
      const m = Math.floor((diff % 3600000) / 60000);
      const s = Math.floor((diff % 60000) / 1000);
      const pad = n => String(n).padStart(2, '0');
      const dEl = el.querySelector('[data-d]'); if (dEl) dEl.textContent = pad(d);
      const hEl = el.querySelector('[data-h]'); if (hEl) hEl.textContent = pad(h);
      const mEl = el.querySelector('[data-m]'); if (mEl) mEl.textContent = pad(m);
      const sEl = el.querySelector('[data-s]'); if (sEl) sEl.textContent = pad(s);
    };
    tick();
    setInterval(tick, 1000);
  });
}

/* ── Counter Animations (About page stats) ───────────────── */
function initCounterAnimations() {
  const counters = document.querySelectorAll('[data-counter]');
  if (!counters.length) return;
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const target = parseInt(el.dataset.counter);
      const suffix = el.dataset.suffix || '';
      let current = 0;
      const step = Math.ceil(target / 80);
      const timer = setInterval(() => {
        current = Math.min(current + step, target);
        el.textContent = current.toLocaleString() + suffix;
        if (current >= target) clearInterval(timer);
      }, 20);
      observer.unobserve(el);
    });
  }, { threshold: 0.4 });
  counters.forEach(el => observer.observe(el));
}

/* ── Cart count real-time update ─────────────────────────── */
function initCartUpdates() {
  // Update cart badge on page load if available
  const cartCountEl = document.getElementById('cartCount');
  if (cartCountEl && cartCountEl.textContent === '0') {
    cartCountEl.style.display = 'none';
  }
}
