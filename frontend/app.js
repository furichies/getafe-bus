function registrarUsuario() {
    const data = {
        nombre: document.getElementById('nombre').value,
        dni: document.getElementById('dni').value,
        email: document.getElementById('email').value
    };
    fetch('http://localhost:5000/api/usuarios/registro', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => alert(`Contraseña generada: ${data.contraseña}`));
}

function login() {
    const data = {
        dni: document.getElementById('login-dni').value,
        contraseña: document.getElementById('login-password').value
    };
    fetch('http://localhost:5000/api/usuarios/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.user_id) {
            localStorage.setItem('user_id', data.user_id);
            window.location.href = 'dashboard.html';
        }
    });
}

function cargarProductos(categoria) {
    fetch(`http://localhost:5001/api/productos?categoria=${categoria}`)
        .then(response => response.json())
        .then(productos => {
            const container = document.getElementById('productos-container');
            container.innerHTML = productos.map(p => `
                <div>
                    <h3>${p.nombre}</h3>
                    <select id="proveedor-${p.id}">
                        ${p.proveedores.map(pr => `<option value="${pr.proveedor}" data-precio="${pr.precio}">${pr.proveedor} - $${pr.precio}</option>`).join('')}
                    </select>
                    <input type="number" id="cantidad-${p.id}" value="1">
                    <button onclick="addToCart('${p.id}')">Añadir</button>
                </div>
            `).join('');
        });
}

function addToCart(productId) {
    const user_id = localStorage.getItem('user_id');
    const proveedor = document.querySelector(`#proveedor-${productId}`).value;
    const precio = document.querySelector(`#proveedor-${productId} option:checked`).dataset.precio;
    const cantidad = document.querySelector(`#cantidad-${productId}`).value;

    fetch('http://localhost:5002/api/cart/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id, product_id: productId, proveedor, cantidad, precio })
    });
}
