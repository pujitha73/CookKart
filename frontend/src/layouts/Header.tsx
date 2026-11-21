import { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { LogOut, Menu, Shield, ShoppingBasket, ShoppingCart, X } from 'lucide-react'
import { Button, ButtonLink } from '../components/Button'
import { GlobalSearch } from '../components/GlobalSearch'
import { useAdminAccess } from '../features/admin/AdminAccessContext'
import { useAuth } from '../features/auth/AuthContext'
import { useCart } from '../features/cart/CartContext'

const navItems = [
  { to: '/shop', label: 'Shop' },
  { to: '/recipes', label: 'Explore Recipes' },
  { to: '/my-kitchen', label: 'My Kitchen' },
  { to: '/orders', label: 'Orders' },
]

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `rounded-full px-3 py-2 text-[15px] font-semibold transition-colors ${
    isActive ? 'bg-sage-muted text-forest-dark' : 'text-forest hover:bg-white/70 hover:text-forest-dark'
  }`

export function Header() {
  const [open, setOpen] = useState(false)
  const [signingOut, setSigningOut] = useState(false)
  const { user, isLoading, signOut } = useAuth()
  const { isAdmin } = useAdminAccess()
  const { itemCount } = useCart()
  const navigate = useNavigate()

  const displayName =
    (user?.user_metadata?.full_name as string | undefined)?.trim() || user?.email || 'Account'

  function cartLink() {
    return (
      <Link
        to="/cart"
        className="relative inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-forest ring-1 ring-forest/10 transition hover:bg-white hover:text-forest-dark"
        aria-label={`Shopping cart, ${itemCount} item${itemCount === 1 ? '' : 's'}`}
      >
        <ShoppingCart size={18} aria-hidden="true" />
        <span className="absolute -right-1 -top-1 flex min-h-5 min-w-5 items-center justify-center rounded-full bg-lime px-1 text-[11px] font-bold text-forest-dark ring-2 ring-cream">
          {itemCount}
        </span>
      </Link>
    )
  }

  async function handleLogout() {
    setSigningOut(true)
    await signOut()
    setSigningOut(false)
    setOpen(false)
    navigate('/', { replace: true })
  }

  return (
    <header className="sticky top-0 z-50 border-b border-forest/10 bg-cream/85 backdrop-blur-md">
      <div className="container-page">
        <div className="flex h-18 items-center justify-between gap-3 py-3">
          <div className="flex items-center gap-3">
            <button
              type="button"
              className="inline-flex h-10 w-10 items-center justify-center rounded-full text-forest ring-1 ring-forest/10 hover:bg-white md:hidden"
              aria-label={open ? 'Close menu' : 'Open menu'}
              aria-expanded={open}
              aria-controls="mobile-nav"
              onClick={() => setOpen((v) => !v)}
            >
              {open ? <X size={18} /> : <Menu size={18} />}
            </button>
            <Link to="/" className="flex items-center gap-2 rounded-full pr-2">
              <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-forest text-lime shadow-[var(--shadow-soft)]">
                <ShoppingBasket size={18} aria-hidden="true" />
              </span>
              <span className="leading-none">
                <span className="block font-display text-xl text-forest-dark">CookKart</span>
                <span className="block text-[11px] font-semibold uppercase tracking-[0.16em] text-forest/70">Groceries & Recipes</span>
              </span>
            </Link>
          </div>

          <nav className="hidden items-center gap-1 md:flex" aria-label="Primary">
            {navItems.map((item) => (
              <NavLink key={item.to} to={item.to} className={navLinkClass}>
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="hidden items-center gap-2 xl:flex">
            {cartLink()}
            <GlobalSearch variant="desktop" />
            {!isLoading && user ? (
              <>
                <span className="max-w-[10rem] truncate text-sm font-semibold text-forest-dark" title={displayName}>{displayName}</span>
                <Button variant="ghost" size="md" onClick={handleLogout} disabled={signingOut}>
                  <LogOut size={16} aria-hidden="true" /> {signingOut ? 'Logging out…' : 'Log out'}
                </Button>
              </>
            ) : !isLoading ? (
              <>
                <ButtonLink to="/login" variant="ghost" size="md">Log in</ButtonLink>
                <ButtonLink to="/signup" variant="primary" size="md">Sign up</ButtonLink>
              </>
            ) : (
              <span className="text-sm text-forest/60">Loading…</span>
            )}
            {isAdmin ? (
              <ButtonLink to="/admin" variant="ghost" size="md" title="Open admin console">
                <Shield size={16} aria-hidden="true" /> Admin
              </ButtonLink>
            ) : null}
          </div>

          <div className="flex items-center gap-2 xl:hidden">
            {cartLink()}
            {!isLoading && user ? (
              <Button variant="ghost" size="md" onClick={handleLogout} disabled={signingOut}>
                <LogOut size={16} aria-hidden="true" /> {signingOut ? '…' : 'Log out'}
              </Button>
            ) : (
              <ButtonLink to="/login" variant="ghost" size="md">Log in</ButtonLink>
            )}
            {isAdmin ? (
              <ButtonLink to="/admin" variant="ghost" size="md" title="Open admin console">
                <Shield size={16} aria-hidden="true" /> Admin
              </ButtonLink>
            ) : null}
          </div>
        </div>

        {open ? (
          <div id="mobile-nav" className="border-t border-forest/10 pb-4 pt-3 md:hidden">
            <div className="mb-3">
              <GlobalSearch variant="mobile" onNavigate={() => setOpen(false)} />
            </div>
            <nav className="flex flex-col gap-1" aria-label="Mobile primary">
              {navItems.map((item) => (
                <NavLink key={item.to} to={item.to} className={navLinkClass} onClick={() => setOpen(false)}>
                  {item.label}
                </NavLink>
              ))}
            </nav>
            <div className="mt-3 flex flex-wrap items-center gap-2">
              {!isLoading && user ? (
                <>
                  <span className="w-full text-sm font-semibold text-forest-dark">{displayName}</span>
                  <Button variant="primary" size="md" onClick={handleLogout} disabled={signingOut}>
                    {signingOut ? 'Logging out…' : 'Log out'}
                  </Button>
                </>
              ) : (
                <ButtonLink to="/signup" variant="primary" size="md" onClick={() => setOpen(false)}>Sign up</ButtonLink>
              )}
              {isAdmin ? (
                <ButtonLink to="/admin" variant="ghost" size="md" onClick={() => setOpen(false)}>
                  <Shield size={16} aria-hidden="true" /> Admin console
                </ButtonLink>
              ) : null}
            </div>
          </div>
        ) : null}
      </div>
    </header>
  )
}
