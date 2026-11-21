import { ArrowLeft, LayoutDashboard, Package, ShoppingBag } from 'lucide-react'
import { NavLink, Outlet } from 'react-router-dom'
import { ButtonLink } from '../components/Button'

const adminNav = [
  { to: '/admin', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/admin/orders', label: 'Orders', icon: ShoppingBag, end: false },
  { to: '/admin/products', label: 'Products', icon: Package, end: false },
]

const navClass = ({ isActive }: { isActive: boolean }) =>
  `inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold transition-colors ${
    isActive ? 'bg-forest text-cream' : 'bg-white/70 text-forest ring-1 ring-forest/10 hover:bg-white'
  }`

export function AdminLayout() {
  return (
    <div className="border-b border-forest/10 bg-cream/60">
      <div className="container-page py-8 md:py-10">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="eyebrow">CookKart admin</p>
            <h1 className="mt-2 font-display text-3xl text-forest-dark md:text-4xl">Operations console</h1>
            <p className="mt-2 max-w-xl text-sm text-forest/75">
              Manage real customer orders and product availability. Changes here are saved to the database immediately.
            </p>
          </div>
          <ButtonLink to="/" variant="ghost" size="md">
            <ArrowLeft size={16} aria-hidden="true" /> Back to store
          </ButtonLink>
        </div>

        <nav className="mt-6 flex flex-wrap gap-2" aria-label="Admin sections">
          {adminNav.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.end} className={navClass}>
              <item.icon size={16} aria-hidden="true" /> {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="mt-6">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
