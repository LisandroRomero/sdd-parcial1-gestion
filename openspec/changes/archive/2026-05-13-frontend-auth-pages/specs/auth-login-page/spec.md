## ADDED Requirements

### Requirement: El usuario puede iniciar sesión desde la página /login

El sistema SHALL proveer una página en la ruta `/login` con un formulario que reciba email y password, llame a `POST /api/v1/auth/login`, guarde los tokens en `useAuthStore` y redirija al usuario a `/` tras un login exitoso.

#### Scenario: Login exitoso redirige a home

- **WHEN** el usuario completa el formulario con credenciales válidas y envía el formulario
- **THEN** el sistema llama a `POST /api/v1/auth/login`, guarda `access_token`, `refresh_token` y datos del usuario en `useAuthStore`, y redirige a `/`

#### Scenario: Login con credenciales incorrectas muestra mensaje de error

- **WHEN** el backend responde con HTTP 401
- **THEN** el sistema muestra el mensaje "Email o contraseña incorrectos" bajo el formulario, sin limpiar los campos

#### Scenario: Login con campos vacíos muestra validación inline

- **WHEN** el usuario intenta enviar el formulario con el campo email o password vacío
- **THEN** el sistema muestra un mensaje de error de validación bajo el campo correspondiente y no envía la request

#### Scenario: Login con email inválido muestra error de formato

- **WHEN** el usuario ingresa un texto que no tiene formato de email válido
- **THEN** el sistema muestra "Ingresá un email válido" bajo el campo email

#### Scenario: El botón Submit muestra estado de carga durante el request

- **WHEN** el formulario está siendo procesado (request en vuelo)
- **THEN** el botón de submit muestra un indicador de loading y queda deshabilitado para evitar doble envío

### Requirement: La página /login provee navegación a /register

El sistema SHALL mostrar un enlace a la página de registro en la página de login para usuarios nuevos.

#### Scenario: Link a registro visible

- **WHEN** el usuario visualiza la página `/login`
- **THEN** ve un enlace "¿No tenés cuenta? Registrate" que navega a `/register`
