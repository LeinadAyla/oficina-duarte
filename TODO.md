# TODO - Ajuste de inicialização do Flask/SQLAlchemy

- [x] Ler `app.py`, `models.py` e verificar onde o Flask cria o banco.
- [x] Identificar causa do erro: `db.create_all()`/queries sem `app.app_context()` e/ou importação de models fora do app.
- [x] Ajustar o final de `app.py` para:
  - [ ] Importar `models` dentro do `with app.app_context():`
  - [ ] Executar `db.create_all()` dentro do mesmo contexto
  - [ ] Manter `app.run()` fora/ao final.
- [ ] (Após mudança) Reiniciar o servidor e validar:
  - [ ] `python app.py` não deve gerar `no such table: clientes`
  - [ ] `db.create_all()` deve criar tabelas do zero no `oficina.db`.

