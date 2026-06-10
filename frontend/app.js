const state = {
  token: localStorage.getItem("campus_market_token") || "",
  user: JSON.parse(localStorage.getItem("campus_market_user") || "null"),
  categories: [],
  items: [],
  editingItemId: null,
};

const API_BASE_URL = window.API_BASE_URL || "";

const els = {
  itemsGrid: document.querySelector("#items-grid"),
  categoryFilter: document.querySelector("#category-filter"),
  publishCategory: document.querySelector("#publish-category"),
  publishForm: document.querySelector("#publish-form"),
  publishMode: document.querySelector("#publish-mode"),
  submitBtn: document.querySelector("#submit-btn"),
  cancelEditBtn: document.querySelector("#cancel-edit-btn"),
  entryState: document.querySelector("#entry-state"),
  accountLink: document.querySelector("#account-link"),
  accountAvatar: document.querySelector("#account-avatar"),
  accountName: document.querySelector("#account-name"),
  accountRole: document.querySelector("#account-role"),
  openAuthInline: document.querySelector("#open-auth-inline"),
  detailModal: document.querySelector("#detail-modal"),
  detailContent: document.querySelector("#detail-content"),
  authModal: document.querySelector("#auth-modal"),
  aiTip: document.querySelector("#ai-tip"),
};

function roleLabel(role) {
  return {
    admin: "管理员",
    student: "校园用户",
  }[role] || "校园用户";
}

function statusLabel(status) {
  return {
    on_sale: "在售",
    reserved: "已预订",
    sold: "已售出",
    off_shelf: "已下架",
  }[status] || status;
}

function conditionLabel(condition) {
  return {
    new: "接近全新",
    good: "成色良好",
    fair: "正常使用痕迹",
  }[condition] || condition;
}

function withAuth(headers = {}) {
  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }
  return headers;
}

async function request(url, options = {}) {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    headers: {
      "Content-Type": "application/json",
      ...withAuth(options.headers || {}),
    },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || data.message || "请求失败");
  }
  return data;
}

function persistAuth() {
  localStorage.setItem("campus_market_token", state.token);
  localStorage.setItem("campus_market_user", JSON.stringify(state.user));
}

function canManageItem(item) {
  return Boolean(
    state.user &&
      item &&
      item.seller &&
      (item.seller.id === state.user.id || state.user.role === "admin"),
  );
}

function showTip(text, target = els.aiTip) {
  target.textContent = text;
}

function toggleModal(element, visible) {
  element.classList.toggle("hidden", !visible);
}

function toggleAuthModal(visible) {
  toggleModal(els.authModal, visible);
}

function resetPublishForm() {
  state.editingItemId = null;
  els.publishForm.reset();
  if (state.categories.length) {
    els.publishCategory.value = String(state.categories[0].id);
  }
  document.querySelector("#condition-level").value = "good";
  els.publishMode.textContent = "新发布的商品会立即出现在商品广场和你的账户中心里。";
  els.submitBtn.textContent = "发布商品";
  els.cancelEditBtn.classList.add("hidden");
  history.replaceState({}, "", "/");
}

function hydrateEntryState() {
  if (!state.user) {
    els.entryState.innerHTML = "<p>当前以游客身份浏览，可以直接查看商品，也可以登录后发布、收藏和留言。</p>";
    els.accountLink.classList.add("hidden");
    els.openAuthInline.classList.remove("hidden");
    return;
  }
  els.entryState.innerHTML = `<p>当前登录身份：<strong>${roleLabel(state.user.role)}</strong>。你可以发布商品，也可以点击右侧头像进入独立账户中心。</p>`;
  els.accountAvatar.src = state.user.avatar || "";
  els.accountName.textContent = state.user.username;
  els.accountRole.textContent = roleLabel(state.user.role);
  els.accountLink.classList.remove("hidden");
  els.openAuthInline.classList.add("hidden");
}

function renderCategories() {
  const options = ['<option value="">全部分类</option>']
    .concat(state.categories.map((item) => `<option value="${item.id}">${item.name}</option>`))
    .join("");
  els.categoryFilter.innerHTML = options;
  els.publishCategory.innerHTML = state.categories
    .map((item) => `<option value="${item.id}">${item.name}</option>`)
    .join("");
  if (!state.editingItemId && state.categories.length) {
    els.publishCategory.value = String(state.categories[0].id);
  }
}

function cardTemplate(item) {
  return `
    <article class="card" data-item-id="${item.id}">
      <img class="card__image" src="${item.image_url || ""}" alt="${item.title}" />
      <div class="card__body">
        <div class="card__meta">
          <span>${item.category.name}</span>
          <span class="status status--${item.status}">${statusLabel(item.status)}</span>
        </div>
        <h3 class="card__title">${item.title}</h3>
        <p class="card__desc">${item.description}</p>
        <div class="card__meta">
          <strong class="price">¥${item.price.toFixed(2)}</strong>
          <span>${item.favorite_count} 收藏 / ${item.message_count} 留言</span>
        </div>
      </div>
    </article>
  `;
}

function renderItems(items) {
  if (!items.length) {
    els.itemsGrid.innerHTML = `<div class="dashboard-card"><p>当前没有符合条件的商品，试试切换筛选条件。</p></div>`;
    return;
  }

  els.itemsGrid.innerHTML = items.map(cardTemplate).join("");
  els.itemsGrid.querySelectorAll("[data-item-id]").forEach((card) => {
    card.addEventListener("click", () => openDetail(card.dataset.itemId));
  });
}

async function loadCategories() {
  state.categories = await request("/api/categories");
  renderCategories();
}

async function loadItems() {
  const keyword = document.querySelector("#keyword").value.trim();
  const categoryId = document.querySelector("#category-filter").value;
  const status = document.querySelector("#status-filter").value;
  const params = new URLSearchParams();
  if (keyword) params.set("keyword", keyword);
  if (categoryId) params.set("category_id", categoryId);
  if (status) params.set("status", status);
  const data = await request(`/api/items?${params.toString()}`);
  state.items = data.items;
  renderItems(data.items);
}

async function openDetail(itemId) {
  const detail = await request(`/api/items/${itemId}`);
  const canManage = canManageItem(detail.item);
  els.detailContent.innerHTML = `
    <div class="detail-layout">
      <div class="detail-meta">
        <img class="detail-image" src="${detail.item.image_url || ""}" alt="${detail.item.title}" />
        <div class="dashboard-card">
          <span class="section-heading__tag">卖家信息</span>
          <strong>${detail.item.seller.username}</strong>
          <p>联系方式：${detail.item.seller.phone || "登录后联系"}</p>
        </div>
      </div>
      <div class="detail-meta">
        <div>
          <p class="section-heading__tag">${detail.item.category.name}</p>
          <h2>${detail.item.title}</h2>
        </div>
        <div class="form-actions">
          <span class="status status--${detail.item.status}">${statusLabel(detail.item.status)}</span>
          <strong class="price">¥${detail.item.price.toFixed(2)}</strong>
        </div>
        <p>${detail.item.description}</p>
        <div class="dashboard-card">
          <p>成色：${conditionLabel(detail.item.condition_level)}</p>
          <p>原价：¥${detail.item.original_price.toFixed(2)}</p>
          <p>收藏：${detail.item.favorite_count}，留言：${detail.item.message_count}</p>
        </div>
        <div class="form-actions">
          <button class="btn btn--primary" onclick="favoriteItem(${detail.item.id})">收藏商品</button>
          ${
            canManage
              ? `<button class="btn btn--ghost" onclick="markSold(${detail.item.id})">标记已售</button>`
              : ""
          }
          ${
            canManage
              ? `<button class="btn btn--ghost" onclick="goEditFromDetail(${detail.item.id})">编辑商品</button>`
              : ""
          }
        </div>
        <div class="detail-section">
          <h3>留言区</h3>
          <div class="message-list">
            ${
              detail.messages.length
                ? detail.messages
                    .map(
                      (msg) => `
                        <div class="message-item">
                          <strong>${msg.sender.username}</strong>
                          <span>${msg.content}</span>
                        </div>
                      `,
                    )
                    .join("")
                : "<p>还没有留言，欢迎第一个咨询。</p>"
            }
          </div>
        </div>
        <form id="message-form" class="detail-section">
          <textarea id="message-content" class="input textarea" placeholder="给卖家留言"></textarea>
          <button class="btn btn--primary" type="submit">发送留言</button>
        </form>
      </div>
    </div>
  `;
  toggleModal(els.detailModal, true);
  document.querySelector("#message-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    await sendMessage(itemId);
  });
}

async function login(mode) {
  const payload = {
    username: document.querySelector("#auth-username").value.trim(),
    password: document.querySelector("#auth-password").value.trim(),
    phone: document.querySelector("#auth-phone").value.trim(),
  };
  const url = mode === "register" ? "/api/auth/register" : "/api/auth/login";
  const body = mode === "register" ? payload : { username: payload.username, password: payload.password };
  const data = await request(url, { method: "POST", body: JSON.stringify(body) });
  state.token = data.token;
  state.user = data.user;
  persistAuth();
  hydrateEntryState();
  toggleAuthModal(false);
  showTip(`欢迎回来，${data.user.username}`);
  const pendingEditId = new URLSearchParams(window.location.search).get("edit");
  if (pendingEditId) {
    await loadEditItem(pendingEditId);
  }
}

async function publishItem(event) {
  event.preventDefault();
  if (!state.token) {
    toggleAuthModal(true);
    return;
  }
  const payload = {
    title: document.querySelector("#title").value.trim(),
    description: document.querySelector("#description").value.trim(),
    price: Number(document.querySelector("#price").value),
    original_price: Number(document.querySelector("#original-price").value || 0),
    condition_level: document.querySelector("#condition-level").value,
    image_url:
      document.querySelector("#image-url").value.trim() ||
      "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?auto=format&fit=crop&w=900&q=80",
    category_id: Number(document.querySelector("#publish-category").value),
  };
  const url = state.editingItemId ? `/api/items/${state.editingItemId}` : "/api/items";
  const method = state.editingItemId ? "PUT" : "POST";
  const data = await request(url, { method, body: JSON.stringify(payload) });
  showTip(data.message);
  resetPublishForm();
  await loadItems();
}

async function generateDescription() {
  const title = document.querySelector("#title").value.trim();
  if (!title) {
    showTip("先输入商品标题，再调用 AI 生成。");
    return;
  }
  const categoryId = Number(document.querySelector("#publish-category").value);
  const category = state.categories.find((item) => item.id === categoryId);
  const data = await request("/api/ai/generate-description", {
    method: "POST",
    body: JSON.stringify({
      title,
      category_name: category ? category.name : "校园闲置",
      condition_level: document.querySelector("#condition-level").value,
      original_price: Number(document.querySelector("#original-price").value || 0),
      expected_price: Number(document.querySelector("#price").value || 0),
    }),
  });
  document.querySelector("#description").value = data.description;
  showTip(`${data.suggested_price_text}。亮点：${data.highlights.join(" / ")}`);
}

async function favoriteItem(itemId) {
  if (!state.token) {
    toggleAuthModal(true);
    return;
  }
  const data = await request(`/api/favorites/${itemId}`, { method: "POST" });
  showTip(data.message);
  await loadItems();
}

async function sendMessage(itemId) {
  if (!state.token) {
    toggleAuthModal(true);
    return;
  }
  const content = document.querySelector("#message-content").value.trim();
  if (!content) return;
  const data = await request(`/api/items/${itemId}/messages`, {
    method: "POST",
    body: JSON.stringify({ content }),
  });
  showTip(data.message);
  await openDetail(itemId);
}

async function markSold(itemId) {
  if (!state.token) {
    toggleAuthModal(true);
    return;
  }
  const data = await request(`/api/items/${itemId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status: "sold" }),
  });
  showTip(data.message);
  toggleModal(els.detailModal, false);
  await loadItems();
}

async function loadEditItem(itemId) {
  if (!state.token) {
    toggleAuthModal(true);
    return;
  }
  const detail = await request(`/api/items/${itemId}`);
  if (!canManageItem(detail.item)) {
    showTip("没有权限编辑这条商品。");
    return;
  }
  state.editingItemId = detail.item.id;
  document.querySelector("#title").value = detail.item.title;
  document.querySelector("#price").value = detail.item.price;
  document.querySelector("#original-price").value = detail.item.original_price || 0;
  document.querySelector("#condition-level").value = detail.item.condition_level;
  document.querySelector("#publish-category").value = String(detail.item.category.id);
  document.querySelector("#image-url").value = detail.item.image_url || "";
  document.querySelector("#description").value = detail.item.description;
  els.publishMode.textContent = `正在编辑：${detail.item.title}`;
  els.submitBtn.textContent = "保存修改";
  els.cancelEditBtn.classList.remove("hidden");
  document.querySelector("#publish-section").scrollIntoView({ behavior: "smooth", block: "start" });
}

function goEditFromDetail(itemId) {
  toggleModal(els.detailModal, false);
  loadEditItem(itemId);
  history.replaceState({}, "", `/?edit=${itemId}`);
}

async function bootstrap() {
  if (state.token) {
    try {
      state.user = await request("/api/auth/me", { headers: {} });
      persistAuth();
    } catch {
      state.token = "";
      state.user = null;
      persistAuth();
    }
  }
  hydrateEntryState();
  await loadCategories();
  resetPublishForm();
  await loadItems();
  const editId = new URLSearchParams(window.location.search).get("edit");
  if (editId && state.token) {
    await loadEditItem(editId);
  }
}

document.querySelector("#refresh-items").addEventListener("click", loadItems);
document.querySelector("#search-btn").addEventListener("click", loadItems);
els.publishForm.addEventListener("submit", publishItem);
document.querySelector("#ai-btn").addEventListener("click", generateDescription);
els.cancelEditBtn.addEventListener("click", resetPublishForm);
document.querySelector("#open-auth").addEventListener("click", () => toggleAuthModal(true));
els.openAuthInline.addEventListener("click", () => toggleAuthModal(true));
document.querySelector("#close-auth").addEventListener("click", () => toggleAuthModal(false));
document.querySelector("#close-detail").addEventListener("click", () => toggleModal(els.detailModal, false));
document.querySelector("#login-btn").addEventListener("click", () => login("login"));
document.querySelector("#register-btn").addEventListener("click", () => login("register"));
document.querySelector("#scroll-publish").addEventListener("click", () => {
  document.querySelector("#publish-section").scrollIntoView({ behavior: "smooth", block: "start" });
});

window.favoriteItem = favoriteItem;
window.markSold = markSold;
window.goEditFromDetail = goEditFromDetail;

bootstrap().catch((error) => {
  showTip(error.message);
});
