import { Link } from 'react-router-dom'
import { ArrowRight, ChefHat, Clock3, ShoppingBag, Sparkles, UtensilsCrossed } from 'lucide-react'
import { ButtonLink } from '../components/Button'
import { Card, FeatureCard } from '../components/Card'
import { ExternalImage } from '../components/ExternalImage'

const heroImage =
  'https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=1600&q=80'

const shoppingImage =
  'https://images.unsplash.com/photo-1543168256-418811576931?auto=format&fit=crop&w=1200&q=80'

const recipeImage =
  'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=1200&q=80'

export function HomePage() {
  return (
    <>
      <section className="relative overflow-hidden border-b border-forest/10 bg-gradient-to-br from-cream via-cream-deep to-sage-muted/40">
        <div className="container-page section-space">
          <div className="grid items-center gap-12 lg:grid-cols-[1.05fr_0.95fr]">
            <div>
              <p className="eyebrow">Premium groceries meet inspired cooking</p>
              <h1 className="mt-4 max-w-2xl text-5xl leading-[1.05] md:text-6xl lg:text-7xl">
                Shop fresh ingredients and discover what to cook, all in one place.
              </h1>
              <p className="mt-6 max-w-xl text-lg leading-relaxed text-forest/80 md:text-xl">
                CookKart brings thoughtful grocery shopping and recipe discovery together in a calm, editorial experience—so every basket can become a beautiful meal.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <ButtonLink to="/shop" variant="primary" size="lg">
                  Start Shopping <ArrowRight size={18} aria-hidden="true" />
                </ButtonLink>
                <ButtonLink to="/recipes" variant="ghost" size="lg">
                  Explore Recipes
                </ButtonLink>
              </div>
              <div className="mt-10 grid gap-4 sm:grid-cols-3">
                {[
                  { label: 'Curated groceries', icon: <ShoppingBag size={18} /> },
                  { label: 'Recipe inspiration', icon: <ChefHat size={18} /> },
                  { label: 'Kitchen-ready planning', icon: <Sparkles size={18} /> },
                ].map((item) => (
                  <div key={item.label} className="flex items-center gap-3 rounded-2xl bg-white/60 p-3 ring-1 ring-forest/10">
                    <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-sage-muted text-forest">{item.icon}</span>
                    <span className="text-sm font-semibold text-forest-dark">{item.label}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative">
              <div className="absolute -left-6 -top-6 h-32 w-32 rounded-full bg-lime/40 blur-2xl" aria-hidden="true" />
              <div className="absolute -bottom-8 -right-4 h-40 w-40 rounded-full bg-sage/40 blur-3xl" aria-hidden="true" />
              <Card className="relative overflow-hidden p-3 md:p-4">
                <ExternalImage
                  src={heroImage}
                  alt="Fresh groceries and produce arranged for cooking"
                  className="h-[360px] w-full rounded-[1rem] object-cover md:h-[520px]"
                  priority
                  sizes="(min-width: 1024px) 45vw, 100vw"
                />
              </Card>
            </div>
          </div>
        </div>
      </section>

      <section className="section-space">
        <div className="container-page">
          <div className="grid items-center gap-10 lg:grid-cols-2">
            <div className="order-2 lg:order-1">
              <Card className="overflow-hidden p-3">
                <ExternalImage
                  src={shoppingImage}
                  alt="A selection of grocery ingredients and pantry staples"
                  className="h-[320px] w-full rounded-[1rem] object-cover md:h-[420px]"
                  sizes="(min-width: 1024px) 45vw, 100vw"
                />
              </Card>
            </div>
            <div className="order-1 lg:order-2">
              <p className="eyebrow">Shop</p>
              <h2 className="mt-3 text-4xl md:text-5xl">A refined grocery experience, designed for everyday cooking.</h2>
              <p className="mt-5 text-lg leading-relaxed text-forest/80">
                Browse produce, pantry staples, and kitchen essentials in a space that feels as considered as the meals you plan to make. CookKart’s shopping experience is being crafted to make finding quality ingredients simple, visual, and enjoyable.
              </p>
              <ul className="mt-6 space-y-3 text-forest/80">
                <li className="flex gap-3"><span className="mt-1 h-2.5 w-2.5 rounded-full bg-lime" aria-hidden="true" /><span>Beautifully presented grocery categories and product discovery.</span></li>
                <li className="flex gap-3"><span className="mt-1 h-2.5 w-2.5 rounded-full bg-lime" aria-hidden="true" /><span>A clear path from inspiration to the ingredients you need.</span></li>
                <li className="flex gap-3"><span className="mt-1 h-2.5 w-2.5 rounded-full bg-lime" aria-hidden="true" /><span>Designed for calm, clutter-free browsing on any device.</span></li>
              </ul>
              <div className="mt-8">
                <ButtonLink to="/shop" variant="secondary">Visit Shop Preview</ButtonLink>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="section-space bg-sage-muted/30 border-y border-forest/10">
        <div className="container-page">
          <div className="grid items-center gap-10 lg:grid-cols-2">
            <div>
              <p className="eyebrow">Explore Recipes</p>
              <h2 className="mt-3 text-4xl md:text-5xl">Discover recipes and see the ingredients behind every dish.</h2>
              <p className="mt-5 text-lg leading-relaxed text-forest/80">
                From comforting classics to quick meal ideas, CookKart is planned to help you explore recipes by collection and meal type—while connecting each dish to the groceries that bring it to life.
              </p>
              <div className="mt-8 grid gap-4 sm:grid-cols-2">
                <FeatureCard
                  icon={<UtensilsCrossed size={20} />}
                  title="Cook with clarity"
                  description="Recipe discovery will highlight the ingredients and details you need before you start."
                  className="bg-white/90"
                />
                <FeatureCard
                  icon={<ChefHat size={20} />}
                  title="Find your next meal"
                  description="Explore collections and meal types in a layout made for browsing and inspiration."
                  className="bg-white/90"
                />
              </div>
              <div className="mt-8">
                <ButtonLink to="/recipes" variant="primary">Explore Recipe Preview</ButtonLink>
              </div>
            </div>
            <div>
              <Card className="overflow-hidden p-3">
                <ExternalImage
                  src={recipeImage}
                  alt="A vibrant prepared meal with fresh ingredients"
                  className="h-[320px] w-full rounded-[1rem] object-cover md:h-[460px]"
                  sizes="(min-width: 1024px) 45vw, 100vw"
                />
              </Card>
            </div>
          </div>
        </div>
      </section>

      <section className="section-space">
        <div className="container-page">
          <div className="mx-auto max-w-3xl text-center">
            <p className="eyebrow">Special Features</p>
            <h2 className="mt-3 text-4xl md:text-5xl">Smart kitchen features for CookKart.</h2>
            <p className="mt-5 text-lg leading-relaxed text-forest/80">
              Connect what’s in your kitchen with what you can cook next. Recipe recommendations and Smart Recipe-to-Cart matching are ready to use with your account.
            </p>
          </div>
          <div className="mt-12 grid gap-6 lg:grid-cols-2">
            <Link to="/my-kitchen" className="block">
              <FeatureCard
                icon={<Clock3 size={22} />}
                eyebrow="Available now"
                badge="Open in My Kitchen"
                title="What Can I Cook Today?"
                description="See recipes ranked by the ingredients you already have, with available and missing items shown on every card."
                className="p-8"
              />
            </Link>
            <Link to="/recipes" className="block">
              <FeatureCard
                icon={<Sparkles size={22} />}
                eyebrow="Available now"
                badge="Open Recipes"
                title="Smart Recipe-to-Cart"
                description="Find the ingredients you are missing, choose from matching grocery products, review your picks, and add them to your account cart."
                className="p-8"
              />
            </Link>
          </div>
          <p className="mt-6 text-center text-sm text-forest/65">
            Sign in and open any recipe to match missing ingredients with products available in the Shop.
          </p>
        </div>
      </section>
    </>
  )
}
