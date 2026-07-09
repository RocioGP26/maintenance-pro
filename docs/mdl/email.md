# MDL · Email Templates

Capítulo completo de correos transaccionales. Todos comparten shell `mtx-email`.

## Shell común (MTX-EML-001)

| Parte | Clase | Contenido |
|-------|-------|-----------|
| Wrapper | `mtx-email` | Tabla 600px max, centrada |
| Header | `mtx-email-header` | Logo MAINTIX + azul `#185FA5` |
| Body | `mtx-email-content` | Copy + CTA |
| Footer | `mtx-email-footer` | Legal, unsubscribe, © |

## Registro de plantillas

| ID | Plantilla | Trigger |
|----|-----------|---------|
| MTX-EML-001 | Shell base | — |
| MTX-EML-010 | Bienvenida | Registro completado |
| MTX-EML-011 | Recuperar contraseña | Reset request |
| MTX-EML-012 | Nueva OT | OT asignada a técnico |
| MTX-EML-013 | Trial | Inicio periodo prueba |
| MTX-EML-014 | Factura | Emisión factura |
| MTX-EML-015 | Pago recibido | Confirmación pago |
| MTX-EML-016 | Empresa creada | Onboarding tenant |
| MTX-EML-017 | Invitación usuario | Admin invita miembro |

## Reglas visuales

1. **Un solo CTA** primary por email (`mtx-btn` inline styles para clientes email).
2. Ancho máximo **600px**.
3. Tipografía: Arial/Helvetica fallback (Inter no fiable en Outlook).
4. Colores inline — no depender de CSS externo.
5. Footer siempre con enlace a soporte y dirección legal.

## Ejemplo · Bienvenida (MTX-EML-010)

```html
<div class="mtx-email">
  <div class="mtx-email-body">
    <div class="mtx-email-header">MAINTIX</div>
    <div class="mtx-email-content">
      <h1 style="font-size:22px;color:#042C53">Bienvenido a Maintix</h1>
      <p>Toda la operación. Una sola plataforma.</p>
      <a href="{{ app_url }}" style="background:#185FA5;color:#fff;padding:12px 24px;border-radius:10px;text-decoration:none;display:inline-block">
        Ir al dashboard
      </a>
    </div>
    <div class="mtx-email-footer">© Maintix · {{ year }}</div>
  </div>
</div>
```

## Jinja

Plantillas en `templates/email/` (futuro). Variables comunes:

- `{{ user_name }}`, `{{ empresa_nombre }}`, `{{ action_url }}`, `{{ year }}`

## Accesibilidad email

- `alt` en logo
- Contraste AA en texto y botones
- No solo imagen para información crítica
