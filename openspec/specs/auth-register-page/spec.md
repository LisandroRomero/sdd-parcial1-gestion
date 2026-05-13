## Requirements

### Requirement: El usuario puede registrarse desde la página /register

El sistema SHALL proveer una página en la ruta `/register` con un formulario que reciba nombre, email, password y confirmación de password, llame a `POST /api/v1/auth/register`, y realice auto-login con los tokens retornados por el backend.

#### Scenario: Registro exitoso hace auto-login y redirige a home

- **WHEN** el usuario completa el formulario con datos válidos y envía el formulario
- **THEN** el sistema llama a `POST /api/v1/auth/register`, usa los tokens de la respuesta para llamar a `useAuthStore.login()`, y redirige a `/`

#### Scenario: Registro con email ya existente muestra error del servidor

- **WHEN** el backend responde con HTTP 409 (Conflict) o 400
- **THEN** el sistema muestra el mensaje de error retornado por el backend bajo el formulario

#### Scenario: Registro con confirmación de password que no coincide bloquea el envío

- **WHEN** el valor del campo "Confirmar password" no coincide con el campo "Password"
- **THEN** el sistema muestra "Las contraseñas no coinciden" bajo el campo de confirmación y no envía la request

#### Scenario: Registro con password demasiado corta muestra error de validación

- **WHEN** el usuario ingresa una password con menos de 8 caracteres
- **THEN** el sistema muestra "La contraseña debe tener al menos 8 caracteres" bajo el campo password

#### Scenario: Campos requeridos vacíos muestran validación inline

- **WHEN** el usuario intenta enviar el formulario con algún campo requerido vacío
- **THEN** el sistema muestra un mensaje de error bajo cada campo vacío y no envía la request

#### Scenario: El botón Submit muestra estado de carga durante el request

- **WHEN** el formulario de registro está siendo procesado
- **THEN** el botón de submit muestra un indicador de loading y queda deshabilitado

### Requirement: La página /register provee navegación a /login

El sistema SHALL mostrar un enlace a la página de login en la página de registro para usuarios con cuenta existente.

#### Scenario: Link a login visible

- **WHEN** el usuario visualiza la página `/register`
- **THEN** ve un enlace "¿Ya tenés cuenta? Iniciá sesión" que navega a `/login`
