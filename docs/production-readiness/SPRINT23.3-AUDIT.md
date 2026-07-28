# Sprint 23.3 · Auditoría inicial y tratamiento

| Hallazgo | Riesgo | Tratamiento |
| --- | --- | --- |
| La suite usaba únicamente SQLite | Diferencias de tipos, DDL y transacciones aparecían al desplegar | Suite completa y migraciones sobre PostgreSQL 18 |
| `TestingConfig` ignoraba bases externas | Era imposible reutilizar la suite contra PostgreSQL | Override exclusivo mediante `TEST_DATABASE_URL` |
| No existía prueba contra un servidor WSGI real | Cookies, redirects y sesiones se validaban solo con test client | Smoke HTTP contra Gunicorn |
| CI no auditaba paquetes vulnerables | Dependencias inseguras podían llegar a producción | Gate `pip-audit --strict` |
| No existía análisis estático de seguridad | Fallos severos podían quedar ocultos | Bandit de severidad alta |
| No existía búsqueda de secretos versionados | Riesgo de publicar credenciales | Gitleaks con historial completo |
| No había revisión automática de cambios de dependencias | Riesgo de cadena de suministro en PR | Dependency Review de GitHub |
| Flask, python-dotenv y PyJWT tenían avisos conocidos | Exposición a vulnerabilidades publicadas | Actualización a versiones corregidas |

## Riesgos residuales

- Los E2E actuales son smoke críticos, no una cobertura visual exhaustiva.
- El servicio PostgreSQL de CI no reproduce extensiones propietarias de Neon.
- Los límites distribuidos, métricas, alertas operativas y workers pertenecen al Sprint 23.4.
