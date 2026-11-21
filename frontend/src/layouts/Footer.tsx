import { Link } from 'react-router-dom'
import { useAdminAccess } from '../features/admin/AdminAccessContext'

export function Footer() {
  const { isAdmin } = useAdminAccess()
  return (
    <footer className="border-t border-forest/10 bg-forest-dark text-cream">
      <div className="container-page py-12">
        <div className="grid gap-10 md:grid-cols-[1.2fr_1fr_1fr]">
          <div>
            <p className="font-display text-2xl text-cream">CookKart</p>
            <p className="mt-3 max-w-md text-sm leading-relaxed text-cream/75">
              A premium grocery and recipe experience designed to bring fresh shopping, inspired cooking, and thoughtful kitchen planning together.
            </p>
          </div>
          <div>
            <h2 className="font-display text-lg text-cream">Explore</h2>
            <ul className="mt-3 space-y-2 text-sm text-cream/80">
              <li><Link to="/shop" className="hover:text-lime">Shop</Link></li>
              <li><Link to="/recipes" className="hover:text-lime">Explore Recipes</Link></li>
              <li><Link to="/my-kitchen" className="hover:text-lime">My Kitchen</Link></li>
              <li><Link to="/cart" className="hover:text-lime">Cart</Link></li>
              <li><Link to="/orders" className="hover:text-lime">Orders</Link></li>
            </ul>
          </div>
          <div>
            <h2 className="font-display text-lg text-cream">Account</h2>
            <ul className="mt-3 space-y-2 text-sm text-cream/80">
              <li><Link to="/login" className="hover:text-lime">Log in</Link></li>
              <li><Link to="/signup" className="hover:text-lime">Sign up</Link></li>
              {isAdmin ? <li><Link to="/admin" className="hover:text-lime">Admin console</Link></li> : null}
            </ul>
            <p className="mt-4 text-xs text-cream/55">Admin access is available only to authorized accounts.</p>
          </div>
        </div>
        <div className="mt-10 border-t border-white/10 pt-6 text-xs text-cream/60">
          <p>© {new Date().getFullYear()} CookKart. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}
