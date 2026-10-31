# ManTAGU live payments (recommended path)

**Do not put bank routing or account numbers in code, git, or env files on the server.**

Stripe collects customer payments (card, and ACH where available) and **payouts to your bank**. You enter routing + account **once** inside the Stripe Dashboard. That is the secure, production-ready way.

Your numbers (use only in Stripe UI):

| Field | Value (enter only in Stripe) |
|-------|------------------------------|
| Routing number | `091017138` |
| Account number | `692101680084` |

---

## 1. Create / open Stripe account

1. Go to [https://dashboard.stripe.com/register](https://dashboard.stripe.com/register)
2. Complete business verification (required for live payouts)
3. Switch to **Live mode** (toggle in the Dashboard)

## 2. Link your bank for payouts (this is where routing + account go)

1. Dashboard → **Settings** → **Payouts** (or **Bank accounts and currency**)
2. **Add bank account**
3. Enter:
   - Routing: `091017138`
   - Account: `692101680084`
4. Confirm ownership (micro-deposits or instant verification if offered)
5. Set payout schedule (daily / weekly — daily is fine once verified)

Stripe will deposit subscription revenue to this account automatically after each successful charge (minus fees).

## 3. Create Products & Prices (subscription tiers)

Dashboard → **Product catalog** → **Add product**

| Product | Recurring price | Env var to set later |
|---------|-----------------|----------------------|
| ManTAGU Starter | **$29 / month** | `STRIPE_PRICE_STARTER=price_...` |
| ManTAGU Pro | **$99 / month** | `STRIPE_PRICE_PRO=price_...` |

Copy each **Price ID** (`price_...`).

Hobby stays free (no Stripe price).

## 4. API keys & webhook

1. **Developers** → **API keys**  
   - Copy **Secret key** (`sk_live_...`) → `STRIPE_SECRET_KEY`
2. **Developers** → **Webhooks** → **Add endpoint**  
   - URL: `https://YOUR_PUBLIC_HOST/v1/billing/webhook`  
   - Events: `checkout.session.completed`, `customer.subscription.*`, `invoice.paid`, `invoice.payment_failed`  
   - Copy **Signing secret** (`whsec_...`) → `STRIPE_WEBHOOK_SECRET`

## 5. Set secrets on your cloud host

Example (Fly.io):

```bash
fly secrets set \
  STRIPE_SECRET_KEY=sk_live_... \
  STRIPE_PRICE_STARTER=price_... \
  STRIPE_PRICE_PRO=price_... \
  STRIPE_WEBHOOK_SECRET=whsec_...
```

Same idea on Render / Railway / Cloud Run (env vars in the service settings).

## 6. Go live with Checkout

Your API already exposes:

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/v1/billing/tiers` | List Hobby / Starter / Pro |
| POST | `/v1/billing/checkout` | Body: `{"tier":"starter","customer_email":"...","success_url":"...","cancel_url":"..."}` → returns Stripe Checkout URL |
| POST | `/v1/billing/portal` | Customer manages card / cancel |
| POST | `/v1/billing/webhook` | Stripe → your server |

Frontend flow:

1. Call `POST /v1/billing/checkout` with tier + email  
2. Redirect browser to the returned `url`  
3. Customer pays → Stripe emails receipt → funds settle to **your linked bank**

## Fees (typical US)

- Card: ~2.9% + $0.30 per successful charge  
- Payouts to your bank: usually free on standard schedule  

Example: $29 Starter → ~$28.00 net before any other costs.

## Security checklist

- [ ] Routing/account **only** in Stripe Dashboard (never in this repo or logs)
- [ ] Live keys only on the server (Fly/Render secrets, not in git)
- [ ] Webhook signature verification enabled (`STRIPE_WEBHOOK_SECRET`)
- [ ] HTTPS only for Checkout success/cancel URLs and webhook

## Local test (optional)

Use Stripe **test mode** keys (`sk_test_...`) and test cards from  
https://stripe.com/docs/testing  

When ready, switch env vars to **live** keys and re-deploy.

---

After steps 1–5, payments are live: customers pay via Checkout, Stripe deposits to routing `091017138` / account `692101680084`.
