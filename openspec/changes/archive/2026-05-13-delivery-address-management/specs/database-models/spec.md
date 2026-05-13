## MODIFIED Requirements

### Requirement: Modelo DireccionEntrega

El sistema SHALL definir el modelo DireccionEntrega en `backend/direcciones/model.py` con FK a usuario_id, alias VARCHAR(50), calle VARCHAR(255), numero VARCHAR(20), piso VARCHAR(20) nullable, departamento VARCHAR(20) nullable, ciudad VARCHAR(100), provincia VARCHAR(100), codigo_postal VARCHAR(20), es_principal BOOLEAN default False, deleted_at TIMESTAMPTZ nullable (soft delete), created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ.

#### Scenario: DireccionEntrega pertenece a un usuario
- **WHEN** se crea una dirección
- **THEN** SHALL tener FK a usuario_id y el sistema garantiza que solo un campo es_principal = True por usuario mediante la lógica del service layer

#### Scenario: DireccionEntrega soporta soft delete
- **WHEN** se elimina una dirección
- **THEN** el sistema SHALL establecer deleted_at = now() en lugar de borrar la fila, y las direcciones con deleted_at NOT NULL SHALL ser excluidas de todos los listados

#### Scenario: DireccionEntrega tiene campos de dirección granulares
- **WHEN** se define el modelo DireccionEntrega
- **THEN** SHALL incluir: alias VARCHAR(50) NOT NULL, calle VARCHAR(255) NOT NULL, numero VARCHAR(20) NOT NULL, piso VARCHAR(20) NULL, departamento VARCHAR(20) NULL, ciudad VARCHAR(100) NOT NULL, provincia VARCHAR(100) NOT NULL, codigo_postal VARCHAR(20) NOT NULL
