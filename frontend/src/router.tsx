import { createBrowserRouter } from 'react-router-dom'
import App from './App'
import { HomePage } from './pages/HomePage'
import { ShopPage } from './pages/ShopPage'
import { ProductDetailPage } from './pages/ProductDetailPage'
import { RecipesPage } from './pages/RecipesPage'
import { RecipeDetailPage } from './pages/RecipeDetailPage'
import { MyKitchenPage } from './pages/MyKitchenPage'
import { CartPage } from './pages/CartPage'
import { CheckoutPage } from './pages/CheckoutPage'
import { OrdersPage } from './pages/OrdersPage'
import { OrderDetailPage } from './pages/OrderDetailPage'
import { LoginPage } from './pages/LoginPage'
import { SignupPage } from './pages/SignupPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { GuestRoute, ProtectedRoute } from './features/auth/ProtectedRoute'
import { AdminRoute } from './features/admin/AdminRoute'
import { AdminLayout } from './layouts/AdminLayout'
import { AdminDashboardPage } from './pages/admin/AdminDashboardPage'
import { AdminOrdersPage } from './pages/admin/AdminOrdersPage'
import { AdminOrderDetailPage } from './pages/admin/AdminOrderDetailPage'
import { AdminProductsPage } from './pages/admin/AdminProductsPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'shop', element: <ShopPage /> },
      { path: 'shop/:slug', element: <ProductDetailPage /> },
      { path: 'recipes', element: <RecipesPage /> },
      { path: 'recipes/:slug', element: <RecipeDetailPage /> },
      {
        element: <ProtectedRoute />,
        children: [
          { path: 'my-kitchen', element: <MyKitchenPage /> },
          { path: 'cart', element: <CartPage /> },
          { path: 'checkout', element: <CheckoutPage /> },
          { path: 'orders', element: <OrdersPage /> },
          { path: 'orders/:orderId', element: <OrderDetailPage /> },
        ],
      },
      {
        element: <AdminRoute />,
        children: [
          {
            path: 'admin',
            element: <AdminLayout />,
            children: [
              { index: true, element: <AdminDashboardPage /> },
              { path: 'orders', element: <AdminOrdersPage /> },
              { path: 'orders/:orderId', element: <AdminOrderDetailPage /> },
              { path: 'products', element: <AdminProductsPage /> },
            ],
          },
        ],
      },
      {
        element: <GuestRoute />,
        children: [
          { path: 'login', element: <LoginPage /> },
          { path: 'signup', element: <SignupPage /> },
        ],
      },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])
