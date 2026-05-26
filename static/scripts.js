document.addEventListener("DOMContentLoaded", () => {
  const panels = document.querySelectorAll(".panel");
  panels.forEach((panel, index) => {
    panel.style.animationDelay = `${index * 0.1}s`;
  });

  setupFormValidation();
  setupSearch();
  setupSorting();
});

// Validación de formularios en tiempo real
function setupFormValidation() {
  const forms = document.querySelectorAll("form");
  forms.forEach(form => {
    const inputs = form.querySelectorAll("input, select");
    inputs.forEach(input => {
      input.addEventListener("blur", () => {
        validateField(input);
      });
      input.addEventListener("input", () => {
        clearFieldError(input);
      });
    });
  });
}

function validateField(field) {
  const value = field.value.trim();
  let isValid = true;
  let message = "";

  if (field.hasAttribute("required") && !value) {
    isValid = false;
    message = "Este campo es obligatorio";
  }

  if (field.type === "number" && value && (isNaN(value) || parseFloat(value) < 0)) {
    isValid = false;
    message = "Debe ser un número positivo";
  }

  if (!isValid) {
    showFieldError(field, message);
  } else {
    clearFieldError(field);
  }

  return isValid;
}

function showFieldError(field, message) {
  field.classList.add("error");
  let errorEl = field.parentElement.querySelector(".error-message");
  if (!errorEl) {
    errorEl = document.createElement("span");
    errorEl.className = "error-message";
    field.parentElement.appendChild(errorEl);
  }
  errorEl.textContent = message;
}

function clearFieldError(field) {
  field.classList.remove("error");
  const errorEl = field.parentElement.querySelector(".error-message");
  if (errorEl) {
    errorEl.remove();
  }
}

// Loading spinners
function showLoading(button) {
  button.disabled = true;
  button.innerHTML = "<i class=\"fas fa-spinner fa-spin\"></i> Cargando...";
}

function hideLoading(button, originalText) {
  button.disabled = false;
  button.innerHTML = originalText;
}

// Notificaciones toast
function showToast(message, type = "info") {
  const toastContainer = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<i class="fas fa-${type === "success" ? "check" : type === "error" ? "times" : "info"}"></i> ${message}`;
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.classList.add("show");
  }, 100);

  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// Confirmaciones
function confirmAction(message) {
  return confirm(message);
}

// Shortcuts de teclado
document.addEventListener("keydown", (e) => {
  if (e.ctrlKey || e.metaKey) {
    switch (e.key) {
      case "d":
        e.preventDefault();
        window.location.href = "/dashboard";
        break;
      case "p":
        e.preventDefault();
        window.location.href = "/productos";
        break;
      case "v":
        e.preventDefault();
        window.location.href = "/ventas";
        break;
    }
  }
});

// Búsqueda en tiempo real
function setupSearch() {
  const searchInputs = document.querySelectorAll(".search-input");
  searchInputs.forEach(input => {
    input.addEventListener("input", (e) => {
      const query = e.target.value.toLowerCase();
      const table = input.closest(".table-wrap").querySelector("tbody");
      const rows = table.querySelectorAll("tr");
      rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(query) ? "" : "none";
      });
    });
  });
}

function setupDebtProductAutocomplete() {
  const productSearch = document.getElementById("product-concept-search");
  const addButton = document.getElementById("product-concept-add");
  const selectedTableBody = document.getElementById("selected-product-rows");
  const debtTotalInput = document.getElementById("monto-total");
  const hiddenConcept = document.getElementById("concepto-hidden");
  const debtForm = document.getElementById("cartera-deuda-form");

  if (!productSearch || !addButton || !selectedTableBody || !debtTotalInput || !hiddenConcept || !debtForm) {
    return;
  }

  const products = window.debtProductOptions || [];
  const selectedProducts = [];

  function findProduct(term) {
    const normalized = term.trim().toLowerCase();
    return products.find(p =>
      p.nombre.toLowerCase() === normalized ||
      p.sku.toLowerCase() === normalized ||
      p.nombre.toLowerCase().includes(normalized) ||
      p.sku.toLowerCase().includes(normalized)
    );
  }

  function updateSummary() {
    const total = selectedProducts.reduce((sum, item) => sum + item.precio_venta * item.quantity, 0);
    const conceptoValue = selectedProducts
      .map(item => `${item.nombre}${item.quantity > 1 ? ` x${item.quantity}` : ""}`)
      .join(", ");

    hiddenConcept.value = conceptoValue;
    debtTotalInput.value = total.toFixed(2);
  }

  function renderSelectedProducts() {
    selectedTableBody.innerHTML = "";

    selectedProducts.forEach((item, index) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${item.nombre}</td>
        <td>${item.sku}</td>
        <td>$${item.precio_venta.toFixed(2)}</td>
        <td><input type="number" min="1" value="${item.quantity}" class="product-qty-input" data-index="${index}" /></td>
        <td>$${(item.precio_venta * item.quantity).toFixed(2)}</td>
        <td><button type="button" class="remove-product" data-index="${index}">Quitar</button></td>
      `;

      const qtyInput = row.querySelector(".product-qty-input");
      const removeButton = row.querySelector(".remove-product");

      qtyInput.addEventListener("change", (e) => {
        const value = parseInt(e.target.value, 10);
        if (Number.isNaN(value) || value < 1) {
          e.target.value = item.quantity;
          return;
        }
        item.quantity = value;
        renderSelectedProducts();
      });

      removeButton.addEventListener("click", () => {
        selectedProducts.splice(index, 1);
        renderSelectedProducts();
      });

      selectedTableBody.appendChild(row);
    });

    updateSummary();
  }

  function addProductByName() {
    const value = productSearch.value.trim();
    if (!value) {
      showToast("Escribe un producto antes de agregar.", "error");
      return;
    }

    const product = findProduct(value);
    if (!product) {
      showToast("Producto no encontrado. Selecciona uno de la lista.", "error");
      return;
    }

    const existing = selectedProducts.find(item => item.sku === product.sku);
    if (existing) {
      existing.quantity += 1;
    } else {
      selectedProducts.push({ ...product, quantity: 1 });
    }

    productSearch.value = "";
    renderSelectedProducts();
  }

  addButton.addEventListener("click", addProductByName);
  productSearch.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addProductByName();
    }
  });

  debtForm.addEventListener("submit", (e) => {
    if (selectedProducts.length === 0) {
      e.preventDefault();
      showToast("Selecciona al menos un producto para registrar la deuda.", "error");
    }
  });
}

// Sorting en tablas
function setupSorting() {
  const tables = document.querySelectorAll("table");
  tables.forEach(table => {
    const headers = table.querySelectorAll("th");
    headers.forEach((header, index) => {
      header.style.cursor = "pointer";
      header.addEventListener("click", () => {
        sortTable(table, index);
      });
    });
  });
}

function sortTable(table, column) {
  const tbody = table.querySelector("tbody");
  const rows = Array.from(tbody.querySelectorAll("tr"));
  const isNumeric = rows.some(row => !isNaN(parseFloat(row.cells[column].textContent)));
  
  rows.sort((a, b) => {
    const aVal = a.cells[column].textContent.trim();
    const bVal = b.cells[column].textContent.trim();
    
    if (isNumeric) {
      return parseFloat(aVal) - parseFloat(bVal);
    } else {
      return aVal.localeCompare(bVal);
    }
  });
  
  rows.forEach(row => tbody.appendChild(row));
}

// Lazy loading (si hay imágenes)
function setupLazyLoading() {
  const images = document.querySelectorAll("img[data-src]");
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.classList.remove("lazy");
        observer.unobserve(img);
      }
    });
  });
  
  images.forEach(img => imageObserver.observe(img));
}

// Atajos de teclado
document.addEventListener("keydown", (e) => {
  // Ctrl + F para foco en búsqueda
  if (e.ctrlKey && e.key === "f") {
    e.preventDefault();
    const searchInput = document.querySelector(".search-input");
    if (searchInput) {
      searchInput.focus();
    }
  }
  
  // Escape para cerrar modales o limpiar búsqueda
  if (e.key === "Escape") {
    const searchInput = document.querySelector(".search-input");
    if (searchInput && document.activeElement === searchInput) {
      searchInput.value = "";
      searchInput.dispatchEvent(new Event("input"));
    }
  }
});

// Ayuda contextual
function showHelp() {
  showToast("Presiona Ctrl+D para Dashboard, Ctrl+P para Productos, Ctrl+V para Ventas", "info");
}

// Inicializar todo
document.addEventListener("DOMContentLoaded", () => {
  setupFormValidation();
  setupSearch();
  setupSorting();
  setupDebtProductAutocomplete();
  setupLazyLoading();
  registerServiceWorker();
  setupOfflineDetection();
});

// Registrar Service Worker para modo offline
function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/sw.js')
      .then((registration) => {
        console.log('Service Worker registrado:', registration);
      })
      .catch((error) => {
        console.log('Error al registrar Service Worker:', error);
      });
  }
}

// Detectar estado de conexión
function setupOfflineDetection() {
  const offlineIndicator = document.getElementById("offline-indicator");
  if (offlineIndicator) {
    window.addEventListener("online", () => {
      offlineIndicator.style.display = "none";
      showToast("Conexión restaurada", "success");
    });
    
    window.addEventListener("offline", () => {
      offlineIndicator.style.display = "inline-block";
      showToast("Sin conexión a internet", "error");
    });
    
    if (!navigator.onLine) {
      offlineIndicator.style.display = "inline-block";
    }
  }
}