"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
document.addEventListener("DOMContentLoaded", () => { const clienteModalElement = document.getElementById("clienteModal"); if (clienteModalElement) {
    clienteModalElement.addEventListener("show.bs.modal", (event) => { const button = event.relatedTarget; if (button) {
        const id = button.getAttribute("data-bs-id");
        const nome = button.getAttribute("data-bs-nome");
        const cpf = button.getAttribute("data-bs-cpf");
        const email = button.getAttribute("data-bs-email");
        const telefone = button.getAttribute("data-bs-telefone");
        const endereco = button.getAttribute("data-bs-endereco");
        const modalTitle = clienteModalElement.querySelector(".modal-title");
        const form = clienteModalElement.querySelector("form");
        if (id) {
            if (modalTitle)
                modalTitle.textContent = "Editar Cliente";
            if (form)
                form.action = `/cliente/editar/${id}`;
            document.getElementById("nome").value = nome || "";
            document.getElementById("cpf").value = cpf || "";
            document.getElementById("email").value = email || "";
            document.getElementById("telefone").value = telefone || "";
            document.getElementById("endereco").value = endereco || "";
        }
        else {
            if (modalTitle)
                modalTitle.textContent = "Novo Cliente";
            if (form) {
                form.action = "/cliente/novo";
                form.reset();
            }
        }
    } });
} });
//# sourceMappingURL=main.js.map