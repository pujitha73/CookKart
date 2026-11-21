import { OrderHistory } from '../features/orders/OrderHistory'

export function OrdersPage() {
  return (
    <section className="section-space">
      <div className="container-page">
        <div className="mx-auto max-w-4xl">
          <div className="mb-8 md:mb-10">
            <p className="eyebrow">Your account</p>
            <h1 className="mt-3 text-4xl md:text-5xl">Your orders</h1>
            <p className="mt-4 max-w-2xl text-lg leading-relaxed text-forest/80">
              Review your Cash on Delivery orders, placing details, and past purchases.
            </p>
          </div>
          <OrderHistory showViewAll={false} title="All orders" />
        </div>
      </div>
    </section>
  )
}
