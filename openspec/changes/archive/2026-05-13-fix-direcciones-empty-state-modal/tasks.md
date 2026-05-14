## 1. Refactor DireccionesList.tsx

- [x] 1.1 Refactor the component to use a `content` variable pattern: assign conditional content (loading/error/empty/grid) to a variable
- [x] 1.2 Move `<DireccionFormModal>` and `<DeleteConfirmDialog>` outside the early returns, rendering them alongside `{content}` inside a React Fragment
- [x] 1.3 Remove the early `return` statements for loading, error, and empty states

## 2. Verify fix

- [x] 2.1 Manual test: open the page with no saved addresses, click "Agregar dirección" — modal should appear
- [x] 2.2 Manual test: with saved addresses, click "Agregar dirección" — modal should appear
- [x] 2.3 Manual test: edit an existing address — modal should appear with pre-filled data
- [x] 2.4 Manual test: delete an address — confirm dialog should appear
- [x] 2.5 Manual test: loading state shows skeleton, error state shows error message with retry

## 3. TypeScript check

- [x] 3.1 Run `npx tsc --noEmit` from the `frontend/` directory to verify no type errors
