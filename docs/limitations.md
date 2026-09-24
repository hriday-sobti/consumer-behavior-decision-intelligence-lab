# Limitations & Boundary Conditions

## 1. Domain Generalizability
- **Wholesale Giftware vs Other Sectors**: The dataset captures transactions from a UK-based online giftware merchant. It should not be generalized to subscription software, retail banking, insurance, or fast-moving consumer goods (FMCG).
- **Wholesale Reseller Concentration**: Many customer IDs represent independent shopkeepers and corporate procurement teams. These commercial entities order in high unit quantities at irregular seasonal intervals.

---

## 2. Unobserved Variables & Observational Bounds
- **No Marketing Intervention History**: The dataset does not record which customers received catalog mailings, promotional emails, volume discounts, or outbound calls.
- **Absence of Customer Motivation**: Observational purchase logs reveal *what* was bought and *when*, but cannot reveal customer intent, satisfaction, or churn motivation.
- **Competitor Activity**: Inactivity may reflect supplier switching, seasonal downtime, inventory rationalization, or business liquidation.

---

## 3. Data-Quality & Behavioral Constraints
- **Unattributed Volume (22.77% of rows)**: Almost 23% of raw line items lack a `customer_id` (walk-ins / guest checkouts). While accounted for at the order and revenue level, these cannot be linked to longitudinal customer accounts.
- **Return & Reversal Dynamics**: Cancellations and returns account for ~2.15% of records. While captured in reversal rates, complex partial product swaps cannot be fully reconstructed.
- **Zero Baseline Discontinuities**: Customers with zero orders in the prior 90-day comparison window have undefined standard percentage momentum; handled via deterministic default rules rather than synthetic interpolations.
