const state = {
  token: localStorage.getItem("campus_market_token") || "",
  user: JSON.parse(localStorage.getItem("campus_market_user") || "null"),
  dashboard: null,
  adminUsers: [],
  managedUser: null,
  managedUserItems: [],
  view: "published",
  userQuery: "",
};

const API_BASE_URL = window.API_BASE_URL || "";

const els = {
  avatar: document.querySelector("#account-avatar"),
  username: document.querySelector("#account-username"),
  roleBadge: document.querySelector("#account-role-badge"),
  summaryInline: document.querySelector("#account-summary-inline"),
  actions: document.querySelector("#account-actions"),
  listTitle: document.querySelector("#account-list-title"),
  listMeta: document.querySelector("#account-list-meta"),
  list: document.querySelector("#account-list"),
  search: document.querySelector("#account-search"),
  backUsers: document.querySelector("#account-back-users"),
  detailModal: document.querySelector("#detail-modal"),
  detailContent: document.querySelector("#detail-content"),
};

function roleLabel(role) {
  return {
    admin: "管理员",
    student: "校园用户",
  }[role] || "游客";
}

function itemStatusLabel(status) {
  return {
    on_sale: "在售",
    reserved: "已预订",
    sold: "已售出",
    off_shelf: "已下架",
  }[status] || status;
}

function userStatusLabel(status) {
  return {
    active: "正常",
    disabled: "已禁用",
  }[status] || status;
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

function canManage(item) {
  return Boolean(
    state.user &&
      item &&
      item.seller &&
      (state.user.role === "admin" || item.seller.id === state.user.id),
  );
}

function collections() {
  const dashboard = state.dashboard || { items: [], favorites: [] };
  const items = dashboard.items || [];
  const favorites = (dashboard.favorites || []).map((entry) => entry.item);
  return {
    published: {
      title: state.user.role === "admin" ? "全站商品" : "我的发布",
      meta: state.user.role === "admin" ? "管理员可管理全部商品" : "你发布的全部商品",
      items,
      empty: "当前没有可展示的商品。",
    },
    on_sale: {
      title: "在售商品",
      meta: "当前正在出售的商品",
      items: items.filter((item) => item.status === "on_sale"),
      empty: "当前没有在售商品。",
    },
    reserved: {
      title: "预订中商品",
      meta: "已被人咨询并预订的商品",
      items: items.filter((item) => item.status === "reserved"),
      empty: "当前没有预订中的商品。",
    },
    sold: {
      title: "已售商品",
      meta: "已经完成交易的商品",
      items: items.filter((item) => item.status === "sold"),
      empty: "当前没有已售商品。",
    },
    off_shelf: {
      title: "已下架商品",
      meta: "暂时不在广场展示的商品",
      items: items.filter((item) => item.status === "off_shelf"),
      empty: "当前没有已下架商品。",
    },
    favorites: {
      title: "我的收藏",
      meta: "你收藏过的商品",
      items: favorites,
      empty: "你还没有收藏商品。",
    },
    messages: {
      title: "收到留言的商品",
      meta: "有留言互动的商品",
      items: items.filter((item) => item.message_count > 0),
      empty: "暂时没有收到留言。",
    },
  };
}

function renderIdentity() {
  if (!state.user) {
    els.summaryInline.innerHTML = "<p>当前未登录，请先返回首页登录。</p>";
    return;
  }
  els.avatar.src = state.user.avatar || "";
  els.username.textContent = state.user.username;
  els.roleBadge.textContent = roleLabel(state.user.role);
  els.roleBadge.classList.toggle("role-badge--admin", state.user.role === "admin");
  els.summaryInline.innerHTML = `
    <p>身份：${roleLabel(state.user.role)}</p>
    <p>账户状态：${userStatusLabel(state.user.status)}</p>
    <p>手机号：${state.user.phone || "未填写"}</p>
  `;
}

function renderActions() {
  if (!state.dashboard) {
    els.actions.innerHTML = "";
    return;
  }
  const data = state.dashboard;
  const cards = [
    ["published", state.user.role === "admin" ? "全站商品" : "我的发布", data.published_count],
    ["on_sale", "在售中", data.on_sale_count],
    ["reserved", "预订中", data.reserved_count],
    ["sold", "已售出", data.sold_count],
    ["off_shelf", "已下架", data.off_shelf_count],
    ["favorites", "我的收藏", data.favorite_count],
    ["messages", "收到留言", data.message_count],
  ];
  if (state.user.role === "admin") {
    cards.push(["users", "用户管理", state.adminUsers.length]);
  }

  els.actions.innerHTML = cards
    .map(([view, label, count]) => {
      const active = view === "users" ? ["users", "user_items"].includes(state.view) : state.view === view;
      return `
        <button class="dashboard-card dashboard-card--action ${active ? "dashboard-card--active" : ""}" data-view="${view}">
          <span class="section-heading__tag">${label}</span>
          <strong>${count}</strong>
        </button>
      `;
    })
    .join("");

  els.actions.querySelectorAll("[data-view]").forEach((button) => {
    button.addEventListener("click", async () => {
      const nextView = button.dataset.view;
      state.view = nextView;
      if (nextView !== "user_items") {
        state.managedUser = null;
        state.managedUserItems = [];
      }
      renderActions();
      renderToolbarControls();
      renderList();
    });
  });
}

function renderToolbarControls() {
  const showUserTools = state.user.role === "admin" && ["users", "user_items"].includes(state.view);
  els.search.classList.toggle("hidden", !showUserTools || state.view !== "users");
  els.backUsers.classList.toggle("hidden", !(showUserTools && state.view === "user_items"));
  els.listMeta.classList.toggle("hidden", showUserTools && state.view === "users");
}

function actionButtons(item) {
  const buttons = [];
  if (canManage(item)) {
    buttons.push(`<a class="btn btn--ghost btn--tiny" href="/?edit=${item.id}">编辑</a>`);
    buttons.push(`<button class="btn btn--ghost btn--tiny" data-action="messages" data-item-id="${item.id}">查看留言</button>`);
    if (item.status === "off_shelf") {
      buttons.push(`<button class="btn btn--primary btn--tiny" data-action="reshelf" data-item-id="${item.id}">重新上架</button>`);
    } else {
      buttons.push(`<button class="btn btn--ghost btn--tiny" data-action="offshelf" data-item-id="${item.id}">下架</button>`);
    }
    buttons.push(`<button class="btn btn--ghost btn--tiny" data-action="delete" data-item-id="${item.id}">删除</button>`);
  }
  return `<div class="mini-card__actions">${buttons.join("")}</div>`;
}

function userActionButtons(user) {
  return `
    <div class="mini-card__actions">
      <button class="btn btn--ghost btn--tiny" data-user-action="items" data-user-id="${user.id}">查看商品</button>
      <button class="btn btn--ghost btn--tiny" data-user-action="${user.status === "active" ? "disable" : "enable"}" data-user-id="${user.id}">
        ${user.status === "active" ? "禁用用户" : "启用用户"}
      </button>
      <button class="btn btn--ghost btn--tiny" data-user-action="delete" data-user-id="${user.id}">删除用户</button>
    </div>
  `;
}

function itemCard(item, metaText) {
  return `
    <article class="mini-card" data-item-id="${item.id}">
      <div class="mini-card__top">
        <div>
          <p class="section-heading__tag">${item.category.name}</p>
          <h3 class="mini-card__title">${item.title}</h3>
        </div>
        <span class="status status--${item.status}">${itemStatusLabel(item.status)}</span>
      </div>
      <p class="mini-card__desc">${item.description}</p>
      <div class="mini-card__meta">
        <strong>¥${item.price.toFixed(2)}</strong>
        <span>${metaText(item)}</span>
      </div>
      ${actionButtons(item)}
    </article>
  `;
}

function userCard(user) {
  return `
    <article class="mini-card" data-user-card="${user.id}">
      <div class="mini-card__top">
        <div>
          <p class="section-heading__tag">普通用户</p>
          <h3 class="mini-card__title">${user.username}</h3>
        </div>
        <span class="status status--${user.status === "disabled" ? "sold" : "on_sale"}">${userStatusLabel(user.status)}</span>
      </div>
      <p class="mini-card__desc">手机号：${user.phone || "未填写"}。已发布 ${user.item_count} 件商品，其中在售 ${user.on_sale_count} 件。</p>
      <div class="mini-card__meta">
        <strong>${user.item_count}</strong>
        <span>创建于 ${new Date(user.created_at).toLocaleDateString("zh-CN")}</span>
      </div>
      ${userActionButtons(user)}
    </article>
  `;
}

function renderItemList(group) {
  const metaText = {
    published: (item) => `卖家：${item.seller.username} / ${item.favorite_count} 收藏`,
    on_sale: (item) => `${item.favorite_count} 收藏 / ${item.message_count} 留言`,
    reserved: (item) => `${item.favorite_count} 收藏 / ${item.message_count} 留言`,
    sold: (item) => `${item.favorite_count} 收藏 / ${item.message_count} 留言`,
    off_shelf: (item) => `卖家：${item.seller.username}`,
    favorites: (item) => `卖家：${item.seller.username}`,
    messages: (item) => `${item.message_count} 条留言`,
    user_items: (item) => `卖家：${item.seller.username} / ${item.message_count} 条留言`,
  }[state.view] || ((item) => `卖家：${item.seller.username}`);

  if (!group.items.length) {
    els.list.innerHTML = `<div class="empty-state">${group.empty}</div>`;
    return;
  }

  els.list.innerHTML = group.items.map((item) => itemCard(item, metaText)).join("");
  els.list.querySelectorAll(".mini-card[data-item-id]").forEach((card) => {
    card.addEventListener("click", () => openDetail(card.dataset.itemId));
  });
  els.list.querySelectorAll("[data-action]").forEach((button) => {
    button.addEventListener("click", async (event) => {
      event.stopPropagation();
      const { action, itemId } = button.dataset;
      if (action === "messages") await openDetail(itemId);
      if (action === "offshelf") await changeStatus(itemId, "off_shelf");
      if (action === "reshelf") await changeStatus(itemId, "on_sale");
      if (action === "delete") await deleteItem(itemId);
    });
  });
}

function renderUserList() {
  const users = state.adminUsers.filter((user) => user.username.toLowerCase().includes(state.userQuery.toLowerCase()));
  els.listTitle.textContent = "普通用户管理";
  els.listMeta.textContent = `当前共有 ${users.length} 位普通用户`;

  if (!users.length) {
    els.list.innerHTML = '<div class="empty-state">没有找到符合条件的普通用户。</div>';
    return;
  }

  els.list.innerHTML = users.map(userCard).join("");
  els.list.querySelectorAll("[data-user-action]").forEach((button) => {
    button.addEventListener("click", async (event) => {
      event.stopPropagation();
      const { userAction, userId } = button.dataset;
      if (userAction === "items") await openManagedUserItems(Number(userId));
      if (userAction === "disable") await updateUserStatus(Number(userId), "disabled");
      if (userAction === "enable") await updateUserStatus(Number(userId), "active");
      if (userAction === "delete") await deleteUser(Number(userId));
    });
  });
}

function renderList() {
  if (state.view === "users") {
    renderUserList();
    return;
  }

  if (state.view === "user_items") {
    const username = state.managedUser ? state.managedUser.username : "该用户";
    renderItemList({
      title: `${username} 发布的商品`,
      items: state.managedUserItems,
      empty: "该用户当前没有发布商品。",
    });
    els.listTitle.textContent = `${username} 发布的商品`;
    els.listMeta.textContent = `共 ${state.managedUserItems.length} 件，可直接管理这些商品`;
    return;
  }

  const group = collections()[state.view] || collections().published;
  els.listTitle.textContent = group.title;
  els.listMeta.textContent = group.meta;
  renderItemList(group);
}

async function openDetail(itemId) {
  const detail = await request(`/api/items/${itemId}`);
  els.detailContent.innerHTML = `
    <div class="detail-layout">
      <div class="detail-meta">
        <img class="detail-image" src="${detail.item.image_url || ""}" alt="${detail.item.title}" />
        <div class="dashboard-card">
          <span class="section-heading__tag">卖家信息</span>
          <strong>${detail.item.seller.username}</strong>
          <p>联系方式：${detail.item.seller.phone || "未填写"}</p>
        </div>
      </div>
      <div class="detail-meta">
        <div>
          <p class="section-heading__tag">${detail.item.category.name}</p>
          <h2>${detail.item.title}</h2>
        </div>
        <div class="form-actions">
          <span class="status status--${detail.item.status}">${itemStatusLabel(detail.item.status)}</span>
          <strong class="price">¥${detail.item.price.toFixed(2)}</strong>
        </div>
        <p>${detail.item.description}</p>
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
                : "<p>还没有留言。</p>"
            }
          </div>
        </div>
      </div>
    </div>
  `;
  els.detailModal.classList.remove("hidden");
}

async function changeStatus(itemId, status) {
  const data = await request(`/api/items/${itemId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
  await loadDashboard();
  if (state.view === "user_items" && state.managedUser) {
    await openManagedUserItems(state.managedUser.id, false);
  }
  alert(data.message);
}

async function deleteItem(itemId) {
  if (!window.confirm("确定删除这条商品吗？")) return;
  const data = await request(`/api/items/${itemId}`, { method: "DELETE" });
  await loadDashboard();
  if (state.view === "user_items" && state.managedUser) {
    await openManagedUserItems(state.managedUser.id, false);
  }
  alert(data.message);
}

async function loadAdminUsers() {
  if (state.user.role !== "admin") {
    state.adminUsers = [];
    return;
  }
  const data = await request("/api/admin/users");
  state.adminUsers = data.users;
}

async function updateUserStatus(userId, status) {
  const data = await request(`/api/admin/users/${userId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
  await loadAdminUsers();
  renderActions();
  renderList();
  alert(data.message);
}

async function deleteUser(userId) {
  if (!window.confirm("确定删除这个普通用户吗？这会同时删除他发布的商品和互动记录。")) return;
  const data = await request(`/api/admin/users/${userId}`, { method: "DELETE" });
  if (state.managedUser && state.managedUser.id === userId) {
    state.view = "users";
    state.managedUser = null;
    state.managedUserItems = [];
  }
  await loadDashboard();
  await loadAdminUsers();
  renderActions();
  renderToolbarControls();
  renderList();
  alert(data.message);
}

async function openManagedUserItems(userId, jump = true) {
  const target = state.adminUsers.find((user) => user.id === userId);
  if (!target) return;
  const data = await request(`/api/admin/users/${userId}/items`);
  state.managedUser = target;
  state.managedUserItems = data.items;
  state.view = "user_items";
  renderActions();
  renderToolbarControls();
  renderList();
  if (jump) {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

async function loadDashboard() {
  state.dashboard = await request("/api/dashboard");
  renderActions();
  renderToolbarControls();
  renderList();
}

function logout() {
  localStorage.removeItem("campus_market_token");
  localStorage.removeItem("campus_market_user");
  window.location.href = "/";
}

async function bootstrap() {
  if (!state.token || !state.user) {
    window.location.href = "/";
    return;
  }
  try {
    state.user = await request("/api/auth/me", { headers: {} });
    localStorage.setItem("campus_market_user", JSON.stringify(state.user));
  } catch {
    window.location.href = "/";
    return;
  }
  renderIdentity();
  await loadDashboard();
  await loadAdminUsers();
  renderActions();
  renderToolbarControls();
  renderList();
}

document.querySelector("#logout-btn").addEventListener("click", logout);
document.querySelector("#close-detail").addEventListener("click", () => {
  els.detailModal.classList.add("hidden");
});
els.search.addEventListener("input", (event) => {
  state.userQuery = event.target.value.trim();
  if (state.view === "users") {
    renderList();
  }
});
els.backUsers.addEventListener("click", () => {
  state.view = "users";
  state.managedUser = null;
  state.managedUserItems = [];
  renderActions();
  renderToolbarControls();
  renderList();
});

bootstrap().catch(() => {
  window.location.href = "/";
});
