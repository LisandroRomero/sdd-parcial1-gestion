# Frontend — Food Store UI (React + TypeScript)

Modern React + TypeScript frontend for the Food Store e-commerce platform using **Feature-Sliced Design (FSD)** architecture.

## 🏗️ Architecture: Feature-Sliced Design (FSD)

Organized in layers from lowest to highest abstraction:

```
frontend/
├── shared/                     # 🔹 Lowest level: reusable primitives
│   ├── api/                    # Axios instance, HTTP utilities
│   ├── components/             # Reusable UI components (buttons, modals, etc.)
│   ├── hooks/                  # Custom React hooks
│   ├── stores/                 # Global Zustand stores (auth, cart, ui)
│   ├── utils/                  # Utility functions
│   └── constants/              # Constants, enums
│
├── entities/                   # 🟡 Domain models and state
│   ├── User/                   # User entity
│   ├── Product/                # Product entity
│   ├── Order/                  # Order entity
│   └── stores/                 # Zustand stores (authStore, cartStore, etc.)
│
├── features/                   # 🟠 Feature-specific logic
│   ├── auth/                   # Login, register, logout
│   ├── products/               # Product listing, filtering
│   ├── cart/                   # Cart management
│   ├── checkout/               # Checkout flow
│   └── orders/                 # Order tracking
│
├── pages/                      # 🟡 Page-level components
│   ├── HomePage.tsx
│   ├── ProductsPage.tsx
│   ├── CartPage.tsx
│   ├── OrdersPage.tsx
│   └── ...
│
├── app/                        # 🔴 Highest level: root app
│   ├── App.tsx                 # Root component
│   ├── Router.tsx              # Route configuration
│   └── providers.tsx           # Global providers (React Query, Theme, etc.)
│
└── public/                     # Static assets (images, favicon, etc.)
```

**Benefits:**
- 📐 Clear separation of concerns
- 🚫 Prevents circular dependencies
- 🔍 Easy to locate code and features
- 🔄 Encourages code reuse
- 🚀 Scales well as the app grows

## 📋 Prerequisites

- **Node.js**: 18+ (or latest LTS)
- **npm**: 9+, **yarn** 4+, or **pnpm** 8+ (choose one)

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your editor
```

**Key variables to set:**
- `VITE_API_BASE_URL`: Backend API URL (e.g., http://localhost:8000/api/v1)
- `VITE_MERCADOPAGO_PUBLIC_KEY`: MercadoPago public key for payments

### 2. Install Dependencies

```bash
# Using npm
npm install

# Or using yarn
yarn install

# Or using pnpm
pnpm install
```

### 3. Start Development Server

```bash
# Using npm
npm run dev

# Or using yarn
yarn dev

# Or using pnpm
pnpm dev
```

Frontend runs on: **http://localhost:5173**

### 4. Build for Production

```bash
npm run build
npm run preview  # Preview production build locally
```

## 🛠️ Development

### Available Scripts

- `npm run dev` — Start development server with hot reload
- `npm run build` — Build optimized production bundle
- `npm run preview` — Preview production build locally
- `npm run lint` — Run ESLint (when configured)
- `npm run type-check` — Type check with TypeScript

### Project Setup

Built with:
- **Vite** — Fast build tool and dev server
- **React 18** — UI library
- **TypeScript** — Type safety
- **TailwindCSS** — Utility-first styling
- **Zustand** — State management
- **React Query** — Server state management
- **Axios** — HTTP client
- **React Router** — Routing

### State Management

#### Zustand Stores (Global Client State)

Located in `entities/stores/`:

1. **authStore** — Authentication state
   - `accessToken`, `refreshToken`, `user`, `isAuthenticated`
   - Methods: `login()`, `logout()`, `updateTokens()`

2. **cartStore** — Shopping cart state
   - `items`, `totalPrice()`
   - Methods: `addItem()`, `removeItem()`, `clearCart()`
   - Persisted to localStorage

3. **paymentStore** — Payment flow state
   - `checkoutStep`, `preferenceId`, `paymentStatus`
   - NOT persisted (ephemeral)

4. **uiStore** — UI state
   - `theme`, `sidebarOpen`, `toasts`
   - Selective persistence (only `theme`)

**Usage:**
```typescript
import { useAuthStore } from '@/entities/stores/authStore';

function MyComponent() {
  const { user, isAuthenticated } = useAuthStore();
  return <div>{user?.name}</div>;
}
```

#### React Query (Server State)

Configure in `app/providers.tsx`:

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,        // 5 minutes
      gcTime: 10 * 60 * 1000,          // 10 minutes
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});
```

**Usage:**
```typescript
import { useQuery } from '@tanstack/react-query';
import { getProducts } from '@/shared/api';

function ProductList() {
  const { data, isLoading } = useQuery({
    queryKey: ['products'],
    queryFn: getProducts,
  });
  
  return <div>{/* ... */}</div>;
}
```

### API Integration

Centralized axios instance in `shared/api/axios.ts`:

```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

// Request interceptor: attach access token
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: handle 401, refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Attempt refresh token
      // If successful: retry original request
      // If fails: redirect to login
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### Styling with TailwindCSS

- No CSS files needed (unless complex animations)
- Use Tailwind utility classes directly in JSX
- Responsive prefixes: `sm:`, `md:`, `lg:`, `xl:`, `2xl:`

```typescript
<button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 md:px-6">
  Click me
</button>
```

### Adding a New Feature

1. **Create feature directory:**
   ```bash
   mkdir frontend/features/my-feature
   mkdir frontend/features/my-feature/{components,hooks}
   ```

2. **Create feature components:**
   ```typescript
   // features/my-feature/components/MyFeature.tsx
   export function MyFeature() {
     return <div>Feature content</div>;
   }
   ```

3. **Create feature hooks** (if needed):
   ```typescript
   // features/my-feature/hooks/useMyFeature.ts
   export function useMyFeature() {
     // Feature logic here
   }
   ```

4. **Create page component:**
   ```typescript
   // pages/MyFeaturePage.tsx
   import { MyFeature } from '@/features/my-feature';
   
   export function MyFeaturePage() {
     return <MyFeature />;
   }
   ```

5. **Add route in router:**
   ```typescript
   // app/Router.tsx
   import { MyFeaturePage } from '@/pages/MyFeaturePage';
   
   const routes = [
     { path: '/my-feature', element: <MyFeaturePage /> },
   ];
   ```

### Component Structure

Example component with TypeScript:

```typescript
// features/products/components/ProductCard.tsx
import { Product } from '@/entities';
import { Button } from '@/shared/components';

interface ProductCardProps {
  product: Product;
  onAddToCart: (product: Product) => void;
}

export function ProductCard({ product, onAddToCart }: ProductCardProps) {
  return (
    <div className="p-4 border rounded shadow hover:shadow-lg transition">
      <img src={product.image} alt={product.name} className="w-full h-48 object-cover rounded" />
      <h3 className="mt-2 font-bold text-lg">{product.name}</h3>
      <p className="text-gray-600 text-sm">{product.description}</p>
      <div className="mt-4 flex justify-between items-center">
        <span className="text-xl font-bold text-green-600">${product.price}</span>
        <Button onClick={() => onAddToCart(product)}>Add to Cart</Button>
      </div>
    </div>
  );
}
```

### Testing (To Be Implemented)

When ready, add:
- **Vitest** — Unit tests
- **React Testing Library** — Component tests
- **Playwright** or **Cypress** — E2E tests

## 🔐 Security

### Protected Routes

Use route guards to protect pages:

```typescript
// HOC: ProtectedRoute.tsx
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '@/entities/stores/authStore';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? children : <Navigate to="/login" />;
}
```

Usage in router:
```typescript
{
  path: '/cart',
  element: <ProtectedRoute><CartPage /></ProtectedRoute>,
}
```

### Token Handling

- Access tokens stored in Zustand (memory + localStorage for persistence)
- Refresh tokens handled by HTTP interceptors
- MercadoPago tokens never passed through backend (PCI compliance)

## 🐛 Debugging

### React DevTools

1. Install [React DevTools Browser Extension](https://react-devtools-tutorial.vercel.app/)
2. Inspect component tree, state, and props

### Zustand DevTools

Store inspection:
```typescript
import { devtools } from 'zustand/middleware';

export const useAuthStore = create<AuthState>()(
  devtools(
    (set) => ({
      // store definition
    }),
    { name: 'authStore' }
  )
);
```

### Network Tab

Monitor API calls in browser DevTools → Network tab:
- Filter by XHR/Fetch
- Check request/response headers and body

## 📚 References

- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [React Query Documentation](https://tanstack.com/query/latest)
- [React Router Documentation](https://reactrouter.com/)
- [FSD Methodology](https://feature-sliced.design/)
