# Versionado de la aplicación Maintix

## Fuentes de verdad separadas

| Producto | Fuente canónica | Changelog | Tag Git |
|---|---|---|---|
| Aplicación Flask | `app/version.py` (`__version__`) | `/CHANGELOG.md` | `vX.Y.Z` |
| Suite documental | `docs/VERSIONS.md` | `docs/changelog.md` | `docs-vX.Y` |

La versión inicial formal de la aplicación es **1.0.0**. La suite documental
continúa en **1.17.0**; ambos ciclos son deliberadamente independientes.

`APP_VERSION` no se configura en Render ni en `.env`: duplicaría la fuente de
verdad y podría hacer que la interfaz, los logs y el código informaran versiones
distintas.

## Dónde consultar la versión

```bash
flask --app run:app version
```

```text
GET /version
GET /api/v1/version
GET /health
```

La UI la muestra discretamente en login, sidebar, panel de plataforma y footer
público. Los endpoints de versión solo publican nombre, versión, release y, si
está disponible, un SHA Git abreviado; no exponen configuración ni secretos.

## Elegir el incremento SemVer

| Incremento | Cuándo usarlo | Ejemplo |
|---|---|---|
| **PATCH** | Corrección compatible, seguridad o ajuste visual sin romper contratos | `1.0.0` → `1.0.1` |
| **MINOR** | Funcionalidad compatible nueva, módulo o endpoint aditivo | `1.0.1` → `1.1.0` |
| **MAJOR** | Cambio incompatible de API, datos, configuración o comportamiento público | `1.1.0` → `2.0.0` |

Una migración de base de datos no obliga por sí sola a subir MAJOR: si es
aditiva y compatible puede ser MINOR o PATCH. Una migración destructiva o un
cambio que exige intervención del cliente sí requiere evaluar MAJOR.

## Flujo de release

1. Partir de `main` actualizado y con el árbol de trabajo limpio.
2. Elegir PATCH, MINOR o MAJOR según la tabla anterior.
3. Cambiar **solo** `__version__` en `app/version.py`.
4. Mover las notas aplicables de `Unreleased` a `[X.Y.Z] - AAAA-MM-DD` en
   `/CHANGELOG.md` y crear nuevamente una sección `Unreleased` vacía.
5. Actualizar la fila «Aplicación Flask» en `docs/VERSIONS.md`. No incrementar
   la suite documental salvo que su contenido también haya cambiado como
   producto.
6. Validar:

   ```bash
   python -m compileall app tests
   python -m pytest -v
   flask --app run:app version
   ```

7. Crear el commit y el tag anotado:

   ```bash
   git add app/version.py CHANGELOG.md docs/VERSIONS.md
   git commit -m "Release vX.Y.Z"
   git tag -a vX.Y.Z -m "Maintix vX.Y.Z"
   git push origin main
   git push origin vX.Y.Z
   ```

8. Crear la release en GitHub desde el tag (interfaz web o, si se usa GitHub
   CLI, `gh release create vX.Y.Z --generate-notes`).
9. Confirmar el despliegue de Render y verificar:

   ```text
   GET https://<servicio>.onrender.com/version
   GET https://<servicio>.onrender.com/health
   ```

   El log de arranque debe incluir `Maintix vX.Y.Z` y el build. Render aporta
   `RENDER_GIT_COMMIT`; GitHub Actions aporta `GITHUB_SHA` automáticamente.

## Render y GitHub

- `render.yaml` despliega `main` con `autoDeploy: true`; el push del commit
  inicia el deploy. El tag documenta exactamente qué commit se liberó.
- La versión viaja en el repositorio, por lo que funciona igual en desarrollo,
  tests, Gunicorn, Render y GitHub Actions.
- El SHA del build es metadato de trazabilidad, no parte del número SemVer.
- Antes de anunciar el release, comprobar que `/version` devuelve el mismo
  `X.Y.Z` que el tag `vX.Y.Z`.

## Hotfix y reversión

Un hotfix parte del último tag estable, incrementa PATCH y sigue el mismo flujo.
Para revertir producción se debe desplegar un commit de reversión seguro; no se
debe mover ni reutilizar un tag publicado.
