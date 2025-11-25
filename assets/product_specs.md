# E-Shop Product Specifications

## Product Catalog

### 1. Wireless Headphones
- **Product ID:** 1
- **Price:** $79.99
- **Description:** Premium wireless headphones with noise cancellation
- **Stock Status:** In Stock
- **Maximum Quantity per Order:** 5

### 2. Smart Watch
- **Product ID:** 2
- **Price:** $149.99
- **Description:** Feature-rich smartwatch with health monitoring
- **Stock Status:** In Stock
- **Maximum Quantity per Order:** 3

### 3. Portable Charger
- **Product ID:** 3
- **Price:** $29.99
- **Description:** 10000mAh portable power bank
- **Stock Status:** In Stock
- **Maximum Quantity per Order:** 10

## Discount Code Rules

### Valid Discount Codes
| Code | Discount | Description |
|------|----------|-------------|
| SAVE15 | 15% | Standard discount for returning customers |
| SAVE10 | 10% | Newsletter subscriber discount |
| WELCOME20 | 20% | First-time customer welcome discount |

### Discount Code Business Rules
1. Only ONE discount code can be applied per order
2. Discount codes are case-insensitive (SAVE15 = save15)
3. Discount is applied to the subtotal BEFORE shipping
4. Discount codes cannot be combined with other promotions
5. Cart must contain at least one item to apply a discount
6. Invalid codes should display an error message: "Invalid discount code"
7. Successfully applied codes should display: "Discount code [CODE] applied! X% off"

## Shipping Options

### Standard Shipping
- **Cost:** FREE
- **Delivery Time:** 5-7 business days
- **Tracking:** Basic tracking provided

### Express Shipping
- **Cost:** $10.00
- **Delivery Time:** 2-3 business days
- **Tracking:** Full tracking with signature confirmation

### Shipping Rules
1. Shipping cost is calculated AFTER discount is applied
2. Express shipping adds $10.00 to the order total
3. Standard shipping is always free regardless of order value

## Payment Methods

### Credit Card
- Accepted cards: Visa, MasterCard, American Express
- Payment is processed immediately upon order submission

### PayPal
- Redirects to PayPal for secure payment
- Supports PayPal balance and linked payment methods

## Order Processing

### Cart Rules
1. Items can be added multiple times (quantity increases)
2. Quantity can be modified using the quantity input field
3. Setting quantity to 0 or clicking "Remove" removes the item
4. Cart persists during the session but clears on page refresh

### Price Calculation Formula
```
Subtotal = Sum of (Item Price × Quantity) for all items
Discount Amount = Subtotal × (Discount Percentage / 100)
Shipping = $0 (Standard) or $10 (Express)
Grand Total = Subtotal - Discount Amount + Shipping
```

### Order Completion
1. Form validation must pass before payment processing
2. Successful payment displays "Payment Successful!" message
3. Order number is generated in format: ORD-[timestamp]
4. Confirmation message indicates email will be sent