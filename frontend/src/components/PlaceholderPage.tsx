import { ButtonLink } from './Button'

type Props = {
  title: string
  description: string
  eyebrow: string
}

export function PlaceholderPage({ title, description, eyebrow }: Props) {
  return (
    <section className="section-space">
      <div className="container-page">
        <div className="mx-auto max-w-3xl card-surface p-8 md:p-12 text-center">
          <p className="eyebrow">{eyebrow}</p>
          <h1 className="mt-3 text-4xl md:text-5xl">{title}</h1>
          <p className="mt-5 text-lg leading-relaxed text-forest/80">{description}</p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <ButtonLink to="/" variant="primary">Back to Home</ButtonLink>
            <ButtonLink to="/shop" variant="ghost">Explore Shop</ButtonLink>
          </div>
        </div>
      </div>
    </section>
  )
}
