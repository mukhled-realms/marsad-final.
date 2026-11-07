<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>مرصد | MARSAD</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.3.2/papaparse.min.js"></script>
<style>
:root {
  --navy: #0F172A; --navy-2: #1E293B; --gold: #C5A021; --gold-light: #FDE047;
  --bg: #F8FAFC; --card: #FFFFFF; --text: #1E293B; --muted: #64748B;
  --line: #E2E8F0; --success: #10B981; --radius: 16px;
  --shadow: 0 4px 6px -1px rgba(0,0,0,.05); --shadow-lg: 0 10px 15px -3px rgba(0,0,0,.1);
}
* { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
body { font-family: 'Tajawal', sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; overflow-x: hidden; }
img, svg { display: block; max-width: 100%; }
a { text-decoration: none; color: inherit; }
button, input, select { font-family: inherit; font-size: inherit; border: none; outline: none; background: none; }

.phone-wrap { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #0F172A; padding: 0; }
.phone { width: 100%; max-width: 430px; height: 100vh; max-height: 920px; background: var(--bg); position: relative; overflow: hidden; display: flex; flex-direction: column; }
@media(min-width: 520px) { .phone { border-radius: 40px; height: 92vh; border: 8px solid var(--navy); box-shadow: 0 25px 50px -12px rgba(0,0,0,.5); } }

.app-header { background: var(--navy); color: #fff; padding: 16px 20px; display: flex; align-items: center; justify-content: space-between; flex-shrink: 0; position: relative; z-index: 100; }
.header-right { display: flex; align-items: center; gap: 12px; }
.menu-btn { font-size: 24px; cursor: pointer; color: var(--gold-light); padding: 4px; }
.brand-title { font-size: 18px; font-weight: 900; }
.brand-sub { font-size: 11px; color: var(--gold); display: block; margin-top: 2px; }
.header-left { display: flex; gap: 8px; }
.icon-btn { width: 38px; height: 38px; border-radius: 50%; background: rgba(255,255,255,.1); display: grid; place-items: center; cursor: pointer; font-size: 18px; color: #fff; }

.status-bar { background: var(--card); padding: 8px 20px; display: flex; align-items: center; justify-content: space-between; font-size: 11.5px; color: var(--muted); border-bottom: 1px solid var(--line); flex-shrink: 0; }
.dot-live { width: 8px; height: 8px; border-radius: 50%; background: var(--success); display: inline-block; margin-left: 6px; }

.ticker-wrap { width: 100%; overflow: hidden; background: var(--gold); color: var(--navy); padding: 6px 0; font-size: 12px; font-weight: 700; white-space: nowrap; flex-shrink: 0; cursor: pointer; }
.ticker { display: inline-block; padding-right: 100%; animation: ticker 25s linear infinite; }
.ticker-wrap:hover .ticker, .ticker-wrap:active .ticker { animation-play-state: paused; }
@keyframes ticker { 0% { transform: translate3d(-100%,0,0); } 100% { transform: translate3d(100%,0,0); } }

.side-drawer-overlay { position: absolute; inset: 0; background: rgba(15,23,42,.6); z-index: 200; opacity: 0; pointer-events: none; transition: .3s; }
.side-drawer-overlay.active { opacity: 1; pointer-events: auto; }
.side-drawer { position: absolute; top: 0; right: -280px; width: 280px; height: 100%; background: var(--navy); z-index: 201; transition: .3s; display: flex; flex-direction: column; padding: 20px; box-shadow: -10px 0 30px rgba(0,0,0,.3); }
.side-drawer.active { right: 0; }
.drawer-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 1px solid rgba(255,255,255,.1); padding-bottom: 15px; }
.drawer-header h2 { font-size: 18px; color: var(--gold); }
.drawer-close { color: #fff; font-size: 24px; cursor: pointer; }
.drawer-menu { display: flex; flex-direction: column; gap: 10px; }
.drawer-item { color: #94A3B8; font-size: 15px; padding: 12px 15px; border-radius: 10px; cursor: pointer; display: flex; align-items: center; gap: 10px; }
.drawer-item:hover, .drawer-item.active { background: rgba(197,160,33,.1); color: var(--gold); }
.drawer-footer { margin-top: auto; text-align: center; color: var(--muted); font-size: 11px; }

.screen { flex: 1; overflow-y: auto; overflow-x: hidden; padding-bottom: 90px; }
.page { display: none; }
.page.active { display: block; animation: fadeIn .3s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.hero { background: var(--navy); color: #fff; padding: 40px 20px; border-radius: 0 0 30px 30px; position: relative; overflow: hidden; text-align: center; }
.hero h1 { font-size: 26px; font-weight: 900; line-height: 1.3; position: relative; z-index: 2; }
.hero h1 em { font-style: normal; color: var(--gold-light); }
.hero p { font-size: 14px; color: #94A3B8; margin-top: 10px; position: relative; z-index: 2; }
.hero-badges { display: flex; justify-content: center; gap: 8px; margin-top: 20px; }
.badge { background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.2); padding: 5px 12px; border-radius: 99px; font-size: 11px; }

.sec-title { padding: 20px 20px 10px; font-size: 18px; font-weight: 900; color: var(--navy); display: flex; justify-content: space-between; }
.product-list { padding: 0 20px; display: flex; flex-direction: column; gap: 12px; }
.product-card { background: var(--card); border-radius: var(--radius); padding: 16px; display: flex; align-items: center; gap: 16px; box-shadow: var(--shadow); border: 1px solid var(--line); cursor: pointer; transition: .2s; }
.product-card:hover { transform: translateY(-2px); border-color: var(--gold); }
.product-icon { width: 55px; height: 55px; border-radius: 12px; background: var(--bg); display: grid; place-items: center; font-size: 26px; flex-shrink: 0; }
.product-info { flex: 1; }
.product-info h3 { font-size: 15px; font-weight: 700; color: var(--navy); }
.product-info p { font-size: 12px; color: var(--muted); }
.product-price { font-size: 16px; font-weight: 900; color: var(--navy); display: flex; align-items: baseline; gap: 3px; flex-shrink: 0; }
.product-price small { font-size: 10px; color: var(--muted); }

.cart-box { background: var(--card); margin: 20px; padding: 20px; border-radius: var(--radius); box-shadow: var(--shadow); border: 1px solid var(--line); }
.cart-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid var(--line); }
.cart-item:last-child { border-bottom: none; }
.cart-item-name { font-size: 14px; font-weight: 700; color: var(--navy); }
.qty-control { display: flex; align-items: center; gap: 12px; background: var(--bg); padding: 4px 8px; border-radius: 8px; }
.qty-btn { width: 26px; height: 26px; border-radius: 6px; background: #fff; border: 1px solid var(--line); font-weight: 900; color: var(--navy); cursor: pointer; }
.cart-total { display: flex; justify-content: space-between; align-items: center; margin-top: 20px; padding-top: 15px; border-top: 2px dashed var(--line); }
.cart-total .total-price { font-size: 22px; font-weight: 900; color: var(--gold); }

.form-box { background: var(--card); margin: 20px; padding: 24px; border-radius: var(--radius); box-shadow: var(--shadow); border: 1px solid var(--line); }
.form-field { margin-bottom: 16px; }
.form-field label { display: block; font-size: 13px; font-weight: 700; color: var(--navy); margin-bottom: 8px; }
.form-field input, .form-field select { width: 100%; padding: 14px; border-radius: 10px; border: 1px solid var(--line); background: var(--bg); font-size: 14px; }
.form-field input:focus, .form-field select:focus { border-color: var(--gold); background: #fff; }
.row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

.btn { display: flex; align-items: center; justify-content: center; padding: 16px; border-radius: 12px; font-weight: 700; font-size: 15px; cursor: pointer; width: 100%; border: none; }
.btn-primary { background: var(--navy); color: var(--gold-light); }
.btn-gold { background: linear-gradient(135deg, var(--gold), #A1821A); color: #fff; }

.map-box { height: 200px; margin: 0 20px 20px; border-radius: var(--radius); overflow: hidden; border: 1px solid var(--line); }

.bottom-nav { position: absolute; bottom: 0; left: 0; right: 0; background: var(--card); border-top: 1px solid var(--line); display: flex; justify-content: space-around; padding: 10px 0 15px; z-index: 100; }
.bnav-item { display: flex; flex-direction: column; align-items: center; gap: 4px; color: var(--muted); font-size: 10px; font-weight: 700; cursor: pointer; position: relative; }
.bnav-item.active { color: var(--navy); }
.bnav-item .icon { font-size: 22px; }
.bnav-item .badge-count { position: absolute; top: -5px; right: -10px; background: var(--gold); color: #fff; width: 18px; height: 18px; border-radius: 50%; display: grid; place-items: center; font-size: 10px; }

.bot-fab { position: absolute; bottom: 90px; left: 20px; width: 56px; height: 56px; border-radius: 50%; background: var(--navy); color: var(--gold); display: grid; place-items: center; font-size: 26px; box-shadow: var(--shadow-lg); cursor: pointer; z-index: 150; border: 2px solid var(--gold); }
.bot-panel { position: absolute; bottom: 90px; left: 20px; right: 20px; height: 400px; background: var(--card); border-radius: var(--radius); box-shadow: var(--shadow-lg); z-index: 151; display: flex; flex-direction: column; overflow: hidden; border: 1px solid var(--line); opacity: 0; pointer-events: none; transform: translateY(20px); transition: .3s; }
.bot-panel.active { opacity: 1; pointer-events: auto; transform: translateY(0); }
.bot-header { background: var(--navy); color: #fff; padding: 15px; display: flex; justify-content: space-between; }
.bot-messages { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; background: var(--bg); }
.msg { max-width: 80%; padding: 10px 14px; border-radius: 12px; font-size: 13px; }
.msg.bot { background: #fff; border: 1px solid var(--line); align-self: flex-start; }
.msg.user { background: var(--navy); color: #fff; align-self: flex-end; }
.bot-input-area { padding: 10px; background: #fff; border-top: 1px solid var(--line); display: flex; gap: 8px; }
.bot-input-area input { flex: 1; padding: 10px 15px; border-radius: 20px; border: 1px solid var(--line); background: var(--bg); font-size: 13px; }
.bot-input-area button { width: 40px; height: 40px; border-radius: 50%; background: var(--gold); color: #fff; display: grid; place-items: center; cursor: pointer; }

#adminPanel { position: absolute; inset: 0; background: var(--navy); color: #fff; z-index: 999; display: none; flex-direction: column; padding: 20px; overflow-y: auto;}
#adminPanel.active { display: flex; }
.admin-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,.1); padding-bottom: 10px; }
.admin-order { background: rgba(255,255,255,.05); padding: 15px; border-radius: 10px; margin-bottom: 10px; font-size: 13px; border-right: 4px solid var(--gold); }
</style>
</head>
<body>

<div class="phone-wrap">
  <div class="phone">
    <header class="app-header">
      <div class="header-right">
        <div class="menu-btn" onclick="toggleDrawer()">☰</div>
        <div>
          <div class="brand-title">مرصد | MARSAD</div>
          <span class="brand-sub">توريد الجملة</span>
        </div>
      </div>
      <div class="header-left">
        <div class="icon-btn" onclick="window.location.href='tel:+966532340613'">📞</div>
        <div class="icon-btn" onclick="window.open('https://wa.me/966532340613', '_blank')">💬</div>
      </div>
    </header>

    <div class="status-bar">
      <div><span class="dot-live"></span> مدير العمليات متواجد</div>
      <div id="loginTime">دخلت: --:--</div>
    </div>

    <div class="ticker-wrap">
      <div class="ticker">🔥 عروض الجملة: أسعار تنافسية للمحلات | 🚚 توصيل سريع | 💳 دفع عند الاستلام | (اضغط على الشريط لإيقافه)</div>
    </div>

    <div class="side-drawer-overlay" id="drawerOverlay" onclick="toggleDrawer()"></div>
    <div class="side-drawer" id="sideDrawer">
      <div class="drawer-header">
        <h2>مرصد | MARSAD</h2>
        <div class="drawer-close" onclick="toggleDrawer()">✕</div>
      </div>
      <div class="drawer-menu">
        <div class="drawer-item active" onclick="nav('home');toggleDrawer()">🏠 الرئيسية</div>
        <div class="drawer-item" onclick="nav('cart');toggleDrawer()">🛒 سلة الطلبات</div>
        <div class="drawer-item" onclick="nav('booking');toggleDrawer()">📝 إتمام الطلب</div>
        <div class="drawer-item" onclick="openAdmin();toggleDrawer()">🔐 لوحة الإدارة (للمدير)</div>
      </div>
      <div class="drawer-footer">مرصد © 2026</div>
    </div>

    <main class="screen" id="mainScreen">
      <section class="page active" id="page-home">
        <div class="hero">
          <h1>وفّر في طلبات محلك.. <br><em>نوفرها لك بالجملة</em></h1>
          <p>نرصد الطلب ونوصل الفرصة.</p>
          <div class="hero-badges">
            <span class="badge">⭐ أسعار جملة</span>
            <span class="badge">⏱️ توصيل سريع</span>
          </div>
        </div>
        <div class="sec-title">🛒 المنتجات المتوفرة</div>
        <div class="product-list" id="productList"></div>
      </section>

      <section class="page" id="page-cart">
        <div class="sec-title">🛒 سلة الطلبات</div>
        <div class="cart-box" id="cartBox">
          <p style="text-align:center; color:var(--muted);">السلة فارغة</p>
        </div>
        <div class="cart-box" id="cartSummary" style="display:none;">
          <div class="cart-total">
            <span>الإجمالي:</span>
            <span class="total-price" id="cartTotalPrice">0.00 ر.س</span>
          </div>
          <button class="btn btn-primary" style="margin-top:15px;" onclick="nav('booking')">✅ متابعة الطلب</button>
        </div>
      </section>

      <section class="page" id="page-booking">
        <div class="sec-title">📝 بيانات الطلب</div>
        <div class="form-box">
          <div class="row-2">
            <div class="form-field"><label>اسم المحل *</label><input type="text" id="bName" placeholder="اسم النشاط"></div>
            <div class="form-field"><label>الجوال *</label><input type="tel" id="bPhone" placeholder="05XXXXXXXX"></div>
          </div>
          <div class="form-field"><label>الموقع / الحي *</label><input type="text" id="bLocation" placeholder="مثال: حي النظيم" readonly></div>
          <div class="row-2">
            <div class="form-field"><label>نوع النشاط</label><select id="bType"><option>بقالة</option><option>مطعم</option><option>كافيه</option></select></div>
            <div class="form-field"><label>الوقت</label><input type="time" id="bTime" value="18:00"></div>
          </div>
          
          <div class="form-field" style="display:flex; align-items:center; gap:10px; margin-top:20px;">
            <input type="checkbox" id="pdplAgree" style="width:20px; height:20px; cursor:pointer;">
            <label for="pdplAgree" style="font-size:12px; color:var(--muted); cursor:pointer; margin-bottom:0;">أوافق على سياسة الخصوصية (PDPL) وأسمح باستخدام بياناتي لتجهيز الطلب.</label>
          </div>

          <button class="btn btn-gold" onclick="submitOrder()" style="margin-top:10px;">🚀 إرسال الطلب عبر واتساب</button>
        </div>
        <div class="sec-title">📍 موقعك (اضغط على الخريطة)</div>
        <div class="map-box" id="map"></div>
      </section>
    </main>

    <div id="adminPanel">
      <div class="admin-header">
        <h2>🔐 لوحة الإدارة (الطلبات)</h2>
        <button onclick="closeAdmin()" style="background:red; color:#fff; padding:5px 10px; border-radius:5px; cursor:pointer;">إغلاق</button>
      </div>
      <div id="adminOrders">
        <p>لا توجد طلبات مسجلة بعد.</p>
      </div>
    </div>

    <div class="bot-fab" onclick="toggleBot()">🤖</div>
    <div class="bot-panel" id="botPanel">
      <div class="bot-header">
        <h3>مساعد مرصد الذكي</h3>
        <div style="cursor:pointer;" onclick="toggleBot()">✕</div>
      </div>
      <div class="bot-messages" id="botMessages">
        <div class="msg bot">أهلاً بك! كيف أقدر أساعدك اليوم؟</div>
      </div>
      <div class="bot-input-area">
        <input type="text" id="botInput" placeholder="اكتب سؤالك..." onkeypress="if(event.key==='Enter') sendBotMsg()">
        <button onclick="sendBotMsg()">➤</button>
      </div>
    </div>

    <nav class="bottom-nav">
      <div class="bnav-item active" id="nav-home" onclick="nav('home')"><span class="icon">🏠</span> الرئيسية</div>
      <div class="bnav-item" id="nav-cart" onclick="nav('cart')"><span class="icon">🛒</span> السلة <span class="badge-count" id="cartBadge" style="display:none;">0</span></div>
      <div class="bnav-item" id="nav-booking" onclick="nav('booking')"><span class="icon">📝</span> الطلب</div>
    </nav>
  </div>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const YEMENI_PHONE = "966532340613";
const ADMIN_PHONE = "966592859590";
let allProducts = [];
let cart = [];
let map, currentMarker;
let ordersDB = JSON.parse(localStorage.getItem('marsad_orders')) || [];

const now = new Date();
document.getElementById('loginTime').innerText = `دخلت: ${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;

Papa.parse("Marsad_Valid_Products.csv", {
  download: true, header: true,
  complete: function(results) {
    allProducts = results.data.filter(row => row['اسم المنتج'] && row['السعر']);
    renderProducts();
  }
});

function renderProducts() {
  const list = document.getElementById('productList');
  list.innerHTML = '';
  allProducts.slice(0, 20).forEach(p => {
    const name = p['اسم المنتج'];
    const price = parseFloat(p['السعر']).toFixed(2);
    const icon = p['القطاع'] === 'بطاقة رقمية' ? '💳' : '📦';
    
    const div = document.createElement('div');
    div.className = 'product-card';
    div.innerHTML = `
      <div class="product-icon">${icon}</div>
      <div class="product-info"><h3>${name}</h3><p>${p['القطاع'] || 'بقالة'}</p></div>
      <div class="product-price">${price}<small>ر.س</small></div>
    `;
    div.onclick = () => addToCart(name, price);
    list.appendChild(div);
  });
}

function addToCart(name, price) {
  const existing = cart.find(item => item.name === name);
  if (existing) existing.qty += 1;
  else cart.push({ name, price, qty: 1 });
  updateCartUI();
  nav('cart');
}

function updateCartUI() {
  const cartBox = document.getElementById('cartBox');
  const cartSummary = document.getElementById('cartSummary');
  const cartTotalPrice = document.getElementById('cartTotalPrice');
  const cartBadge = document.getElementById('cartBadge');

  if (cart.length === 0) {
    cartBox.innerHTML = '<p style="text-align:center; color:var(--muted);">السلة فارغة</p>';
    cartSummary.style.display = 'none';
    cartBadge.style.display = 'none';
    return;
  }

  cartBox.innerHTML = '';
  let total = 0;
  cart.forEach((item, index) => {
    total += item.price * item.qty;
    cartBox.innerHTML += `
      <div class="cart-item">
        <div class="cart-item-name">${item.name}</div>
        <div class="qty-control">
          <button class="qty-btn" onclick="changeQty(${index}, -1)">-</button>
          <span>${item.qty}</span>
          <button class="qty-btn" onclick="changeQty(${index}, 1)">+</button>
        </div>
      </div>
    `;
  });
  cartTotalPrice.innerText = `${total.toFixed(2)} ر.س`;
  cartSummary.style.display = 'block';
  cartBadge.innerText = cart.reduce((sum, item) => sum + item.qty, 0);
  cartBadge.style.display = 'grid';
}

function changeQty(index, change) {
  cart[index].qty += change;
  if (cart[index].qty <= 0) cart.splice(index, 1);
  updateCartUI();
}

function nav(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-' + page).classList.add('active');
  document.querySelectorAll('.bnav-item').forEach(b => b.classList.remove('active'));
  document.getElementById('nav-' + page).classList.add('active');
  document.querySelectorAll('.drawer-item').forEach(b => b.classList.remove('active'));
  if (page === 'home') document.querySelectorAll('.drawer-item')[0].classList.add('active');
  if (page === 'cart') document.querySelectorAll('.drawer-item')[1].classList.add('active');
  if (page === 'booking') document.querySelectorAll('.drawer-item')[2].classList.add('active');
  
  if (page === 'booking') initMap();
  if (page === 'cart') updateCartUI();
  document.getElementById('mainScreen').scrollTop = 0;
}

function toggleDrawer() {
  document.getElementById('sideDrawer').classList.toggle('active');
  document.getElementById('drawerOverlay').classList.toggle('active');
}

function initMap() {
  if (map) return;
  map = L.map('map').setView([24.7136, 46.6753], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
  map.on('click', function(e) {
    if (currentMarker) map.removeLayer(currentMarker);
    currentMarker = L.marker(e.latlng).addTo(map).bindPopup("موقعك").openPopup();
    document.getElementById('bLocation').value = `موقع محدد (${e.latlng.lat.toFixed(4)}, ${e.latlng.lng.toFixed(4)})`;
  });
}

function submitOrder() {
  if (!document.getElementById('pdplAgree').checked) { 
    alert('يرجى الموافقة على سياسة الخصوصية أولاً.'); 
    return; 
  }
  
  if (cart.length === 0) { alert('السلة فارغة!'); return; }
  
  const name = document.getElementById('bName').value;
  const phone = document.getElementById('bPhone').value;
  const location = document.getElementById('bLocation').value;

  if (!name || !phone || !location) { alert('يرجى تعبئة الحقول.'); return; }

  let orderDetails = cart.map(item => `- ${item.name} (${item.qty})`).join('\n');
  let total = cart.reduce((sum, item) => sum + (item.price * item.qty), 0).toFixed(2);
  const orderData = { id: Date.now(), name, phone, location, items: orderDetails, total, date: new Date().toLocaleString('ar-SA') };
  
  ordersDB.push(orderData);
  localStorage.setItem('marsad_orders', JSON.stringify(ordersDB));

  const msg = `مرحباً مرصد، طلب جديد:\n👤 ${name}\n📱 ${phone}\n📍 ${location}\n\n📦 الطلبات:\n${orderDetails}\n\n💰 الإجمالي: ${total} ر.س`;
  
  window.open(`https://wa.me/${YEMENI_PHONE}?text=${encodeURIComponent(msg)}`, '_blank');
  setTimeout(() => { window.open(`https://wa.me/${ADMIN_PHONE}?text=${encodeURIComponent(msg)}`, '_blank'); }, 1000);
  
  cart = [];
  updateCartUI();
  alert('تم تجهيز الطلب! سيتم تحويلك للواتساب.');
  nav('home');
}

function toggleBot() { document.getElementById('botPanel').classList.toggle('active'); }

function sendBotMsg() {
  const input = document.getElementById('botInput');
  const val = input.value.trim();
  if (!val) return;
  botReply(val);
  input.value = '';
}

function botReply(question) {
  const msgs = document.getElementById('botMessages');
  msgs.innerHTML += `<div class="msg user">${question}</div>`;
  msgs.scrollTop = msgs.scrollHeight;
  
  let reply = "عذراً، لم أفهم قصدك. جرب السؤال عن: أسعار المياه، طريقة الطلب، أو تواصل معنا.";
  
  const foundProduct = allProducts.find(p => question.includes(p['اسم المنتج']) || p['اسم المنتج'].includes(question.replace('بكم ', '').replace('سعر ', '').replace('؟','').trim()));
  
  if (foundProduct) {
    reply = `نعم متوفر لدينا ${foundProduct['اسم المنتج']} بسعر ${foundProduct['السعر']} ريال. يمكنك إضافته للسلة!`;
  } else if (question.includes('مياه') || question.includes('مويه') || question.includes('بيرين') || question.includes('نوفا') || question.includes('إيفا')) {
    reply = "لدينا جميع أنواع المياه (بيرين، نوفا، إيفا، صفا). يرجى كتابة اسم المنتج بالكامل لمعرفة سعره.";
  } else if (question.includes('طلب') || question.includes('أطلب')) {
    reply = "للطلب: اختر المنتجات من الرئيسية، ثم اذهب للسلة، أدخل بياناتك، وحدد موقعك على الخريطة.";
  }

  setTimeout(() => {
    msgs.innerHTML += `<div class="msg bot">${reply}</div>`;
    msgs.scrollTop = msgs.scrollHeight;
  }, 600);
}

function openAdmin() {
  const pin = prompt("أدخل رمز الدخول:");
  if (pin === "5590") {
    document.getElementById('adminPanel').classList.add('active');
    renderAdminOrders();
  } else {
    alert("رمز خاطئ!");
  }
}
function closeAdmin() { document.getElementById('adminPanel').classList.remove('active'); }
function renderAdminOrders() {
  const container = document.getElementById('adminOrders');
  if (ordersDB.length === 0) { container.innerHTML = '<p>لا توجد طلبات.</p>'; return; }
  container.innerHTML = ordersDB.map(o => `
    <div class="admin-order">
      <b>${o.name}</b><br>${o.phone}<br>${o.location}<br>
      <small>${o.date}</small><br>
      <pre>${o.items}</pre>
      <b style="color:var(--gold);">الإجمالي: ${o.total} ر.س</b>
    </div>
  `).join('');
}
</script>
</body>
</html>
