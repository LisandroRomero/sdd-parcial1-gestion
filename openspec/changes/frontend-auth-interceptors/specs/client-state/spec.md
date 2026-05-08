## MODIFIED Requirements

### Requirement: authStore — Sesión de usuario

La aplicación SHALL mantener un store de autenticación (`authStore`) que refleje el estado de sesión del cliente en memoria.

El store SHALL exponer:
- `user`: `User | null` — datos del usuario autenticado o null
- `token`: `string | null` — JWT access token o null
- `refreshToken`: `string | null` — JWT refresh token o null (NO persistido)
- `isAuthenticated`: `boolean` — derivado de `token !== null`
- `login(user, accessToken, refreshToken)`: setea user, token y refreshToken
- `logout()`: limpia user, token y refreshToken a null
- `updateUser(user)`: actualiza solo user (ej: después de editar perfil)
- `setTokens(accessToken, refreshToken)`: actualiza ambos tokens sin modificar el user (usado por el interceptor de refresh automático)
- `hasRole(role: string): boolean` — retorna true si el user tiene el rol dado

El store SHALL usar persist middleware (`zustand/middleware`) con `partialize` para persistir SOLO `user` y `token`. El `refreshToken` NO SHALL persistir.

#### Scenario: Login exitoso

- **WHEN** `login(userData, accessToken, refreshToken)` es llamado
- **THEN** `user` SHALL contener `userData`
- **THEN** `token` SHALL contener `accessToken`
- **THEN** `refreshToken` SHALL contener el refresh token
- **THEN** `isAuthenticated` SHALL ser true

#### Scenario: Logout

- **WHEN** `logout()` es llamado
- **THEN** `user` SHALL ser null
- **THEN** `token` SHALL ser null
- **THEN** `refreshToken` SHALL ser null
- **THEN** `isAuthenticated` SHALL ser false

#### Scenario: setTokens actualiza tokens sin tocar el user

- **WHEN** `setTokens(newAccessToken, newRefreshToken)` es llamado
- **THEN** `token` SHALL contener `newAccessToken`
- **THEN** `refreshToken` SHALL contener `newRefreshToken`
- **THEN** `user` SHALL permanecer sin cambios

#### Scenario: hasRole retorna true para rol que el usuario posee

- **WHEN** `hasRole("ADMIN")` es llamado y user tiene `roles: ["ADMIN", "CLIENT"]`
- **THEN** retorna `true`

#### Scenario: hasRole retorna false si no hay usuario autenticado

- **WHEN** `hasRole("ADMIN")` es llamado y `user` es null
- **THEN** retorna `false`

#### Scenario: refreshToken no se persiste al recargar la página

- **WHEN** el usuario hace login y luego recarga la página
- **THEN** `token` (access token) SHALL recuperarse del storage
- **THEN** `refreshToken` SHALL ser null (no se persiste)

#### Scenario: Actualización de perfil

- **WHEN** `updateUser(updatedData)` es llamado
- **THEN** `user` SHALL contener los datos actualizados
- **THEN** `token` SHALL permanecer sin cambios
