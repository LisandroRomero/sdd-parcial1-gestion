## ADDED Requirements

### Requirement: Nuevo usuario se registra con datos básicos

El sistema SHALL permitir que un nuevo usuario se registre proporcionando nombre, apellido, email y contraseña. El usuario registrado SHALL obtener automáticamente el rol `CLIENT`.

#### Scenario: Registro exitoso

- **WHEN** un usuario envía POST /api/v1/auth/register con `{ nombre: "Juan", apellido: "Pérez", email: "juan@example.com", password: "securepass123" }`
- **THEN** el sistema retorna HTTP 201 con un `UserResponse` que incluye `id`, `nombre`, `apellido`, `email`, `roles: ["CLIENT"]` y `created_at`
- **AND** el usuario puede loguearse con esas credenciales

#### Scenario: Email duplicado

- **WHEN** un usuario intenta registrarse con un email que ya existe en la base de datos
- **THEN** el sistema retorna HTTP 409 Conflict con un mensaje indicando que el email ya está registrado

#### Scenario: Password demasiado corto

- **WHEN** un usuario envía un password de menos de 8 caracteres
- **THEN** el sistema retorna HTTP 422 Unprocessable Entity con error de validación en el campo `password`

#### Scenario: Email inválido

- **WHEN** un usuario envía un email con formato inválido
- **THEN** el sistema retorna HTTP 422 Unprocessable Entity con error de validación en el campo `email`

#### Scenario: Nombre o apellido fuera de longitud

- **WHEN** un usuario envía un nombre de menos de 2 caracteres o más de 80 caracteres
- **THEN** el sistema retorna HTTP 422 con error de validación

#### Scenario: Campos faltantes

- **WHEN** un usuario envía el request sin alguno de los campos requeridos (`nombre`, `apellido`, `email`, `password`)
- **THEN** el sistema retorna HTTP 422 con errores de validación por cada campo faltante

### Requirement: Contraseña almacenada de forma segura

El sistema SHALL almacenar la contraseña únicamente como hash bcrypt con costo ≥ 12. NUNCA SHALL almacenar la contraseña en texto plano ni loguearla.

#### Scenario: Hash generado correctamente

- **WHEN** un usuario se registra exitosamente
- **THEN** el campo `password_hash` en la base de datos contiene un hash bcrypt válido (comienza con `$2b$`)

#### Scenario: Contraseña no retornada

- **WHEN** el sistema retorna un `UserResponse` después del registro
- **THEN** la respuesta NO incluye el campo `password_hash` ni `password`

### Requirement: Asignación automática de rol CLIENT

El sistema SHALL asignar el rol `CLIENT` a todo usuario registrado, y SHALL hacerlo en la misma transacción que la creación del usuario.

#### Scenario: Rol asignado en misma transacción

- **WHEN** un usuario se registra exitosamente
- **THEN** existe un registro en `usuario_rol` con `usuario_id` = id del nuevo usuario y `rol_codigo` = `"CLIENT"`
- **AND** si la asignación del rol falla, el usuario NO es creado (rollback)

#### Scenario: Rol CLIENT existe en seed

- **WHEN** el sistema intenta asignar el rol CLIENT
- **THEN** el rol `CLIENT` existe en la tabla `rol` (debe haber sido creado por seed.py)
