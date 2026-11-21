import { useState } from 'react'
import { useAuth } from '../features/auth/AuthContext'
import { PantryManager } from '../features/kitchen/PantryManager'
import { SavedRecipes } from '../features/kitchen/SavedRecipes'
import { WhatCanICookToday } from '../features/kitchen/WhatCanICookToday'
import { OrderHistory } from '../features/orders/OrderHistory'

export function MyKitchenPage() {
  const { user } = useAuth()
  const [pantryVersion, setPantryVersion] = useState(0)
  const name = (user?.user_metadata?.full_name as string | undefined)?.trim()

  return (
    <section className="section-space">
      <div className="container-page">
        <div className="mx-auto max-w-6xl">
          <div className="card-surface p-8 md:p-10">
            <p className="eyebrow">My Kitchen</p>
            <h1 className="mt-3 text-4xl md:text-5xl">
              {name ? `Welcome, ${name}` : 'Welcome to your kitchen'}
            </h1>
            <p className="mt-4 max-w-2xl text-lg leading-relaxed text-forest/80">
              Keep track of the ingredients you have on hand and the recipes you want to cook again.
            </p>
            {user?.email ? (
              <p className="mt-3 text-sm font-semibold text-forest/70">Signed in as {user.email}</p>
            ) : null}
          </div>

          <div className="mt-8 space-y-8">
            <div id="my-pantry">
              <PantryManager onPantryChange={() => setPantryVersion((value) => value + 1)} />
            </div>
            <WhatCanICookToday pantryVersion={pantryVersion} />
            <SavedRecipes />
            <OrderHistory limit={3} />
          </div>
        </div>
      </div>
    </section>
  )
}
