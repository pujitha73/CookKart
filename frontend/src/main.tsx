import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import './index.css'
import { router } from './router'
import { AdminAccessProvider } from './features/admin/AdminAccessContext'
import { AuthProvider } from './features/auth/AuthContext'
import { CartProvider } from './features/cart/CartContext'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <AdminAccessProvider>
        <CartProvider>
          <RouterProvider router={router} />
        </CartProvider>
      </AdminAccessProvider>
    </AuthProvider>
  </StrictMode>,
)
