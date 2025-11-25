# E-Shop Test Scenarios Documentation

## Overview
This document outlines the key test scenarios for the E-Shop checkout application, organized by feature area.

## 1. Product Catalog Tests

### 1.1 Add to Cart Functionality
- **Scenario**: User clicks "Add to Cart" for any product
- **Expected**: Product is added to cart, cart updates to show item
- **Elements**: 
  - Add buttons: `#add-product-1`, `#add-product-2`, `#add-product-3`
  - Cart container: `#cart-items`

### 1.2 Multiple Products
- **Scenario**: User adds multiple different products
- **Expected**: All products appear in cart separately
- **Verification**: Check cart-items container has multiple cart-item elements

### 1.3 Duplicate Product Addition
- **Scenario**: User clicks "Add to Cart" for same product twice
- **Expected**: Product quantity increases to 2, not duplicate entry
- **Verification**: Check quantity input value equals 2

## 2. Shopping Cart Tests

### 2.1 Empty Cart State
- **Scenario**: No products added yet
- **Expected**: Message "Your cart is empty" displayed
- **Element**: `#empty-cart-message`

### 2.2 Quantity Update
- **Scenario**: User changes quantity input value
- **Expected**: Item subtotal and grand total recalculate
- **Element**: `.quantity-input` or `#qty-[productId]`

### 2.3 Remove Item
- **Scenario**: User clicks "Remove" button on cart item
- **Expected**: Item removed, totals recalculate
- **Element**: `#remove-[productId]`

### 2.4 Cart Total Calculation
- **Scenario**: Multiple items in cart with various quantities
- **Expected**: Subtotal = sum of (price × quantity) for all items
- **Verification**: `#subtotal` displays correct value

## 3. Discount Code Tests

### 3.1 Valid Discount Code - SAVE15
- **Precondition**: Cart has at least one item
- **Action**: Enter "SAVE15" and click Apply
- **Expected**: 
  - Success message: "Discount code SAVE15 applied! 15% off"
  - Message has class `discount-success`
  - `#discount-amount` shows 15% of subtotal

### 3.2 Valid Discount Code - SAVE10
- **Precondition**: Cart has at least one item
- **Action**: Enter "SAVE10" and click Apply
- **Expected**: 10% discount applied

### 3.3 Valid Discount Code - WELCOME20
- **Precondition**: Cart has at least one item
- **Action**: Enter "WELCOME20" and click Apply
- **Expected**: 20% discount applied

### 3.4 Invalid Discount Code
- **Precondition**: Cart has at least one item
- **Action**: Enter "INVALID123" and click Apply
- **Expected**:
  - Error message: "Invalid discount code"
  - Message has class `discount-error`
  - No discount applied

### 3.5 Discount on Empty Cart
- **Precondition**: Cart is empty
- **Action**: Enter "SAVE15" and click Apply
- **Expected**: 
  - Error message: "Please add items to cart first"
  - Message has class `discount-error`

### 3.6 Multiple Discount Codes
- **Precondition**: SAVE15 already applied
- **Action**: Try to apply SAVE10
- **Expected**:
  - Error message: "A discount code has already been applied"
  - Original discount remains

### 3.7 Case Insensitivity
- **Precondition**: Cart has items
- **Action**: Enter "save15" (lowercase)
- **Expected**: Discount code works (case insensitive)

## 4. Form Validation Tests

### 4.1 Empty Name Field
- **Action**: Leave name empty, click Pay Now
- **Expected**:
  - `#name-error` becomes visible
  - `#customer-name` has class `input-error`
  - Error text: "Please enter your full name"

### 4.2 Empty Email Field
- **Action**: Leave email empty, click Pay Now
- **Expected**:
  - `#email-error` becomes visible
  - Error text: "Please enter a valid email address"

### 4.3 Invalid Email Format
- **Test Cases**:
  - "john" → Invalid
  - "john@" → Invalid
  - "@example.com" → Invalid
  - "john@example" → Invalid
  - "john@example.com" → Valid

### 4.4 Empty Address Field
- **Action**: Leave address empty, click Pay Now
- **Expected**:
  - `#address-error` becomes visible
  - Error text: "Please enter your shipping address"

### 4.5 Error Clearing on Input
- **Precondition**: Validation error shown
- **Action**: Start typing in the field
- **Expected**: Error message hides, red border removes

### 4.6 All Fields Valid
- **Action**: Fill all required fields correctly, click Pay Now
- **Expected**: Form submits (no validation errors)

## 5. Shipping Method Tests

### 5.1 Standard Shipping (Default)
- **Initial State**: Standard shipping selected by default
- **Expected**: Shipping cost = $0.00
- **Element**: `#shipping-standard` is checked

### 5.2 Express Shipping Selection
- **Action**: Click Express Shipping option
- **Expected**: 
  - `#shipping-express` becomes checked
  - `#shipping-cost` shows "$10.00"
  - Grand total increases by $10

### 5.3 Shipping with Discount
- **Scenario**: Apply SAVE15, select Express
- **Expected**: 
  - Discount applied to subtotal
  - Shipping added AFTER discount
  - Formula: Total = (Subtotal - 15%) + $10

## 6. Payment Method Tests

### 6.1 Credit Card (Default)
- **Initial State**: Credit Card selected
- **Element**: `#payment-credit-card` is checked

### 6.2 PayPal Selection
- **Action**: Click PayPal option
- **Expected**: `#payment-paypal` becomes checked

## 7. Payment Processing Tests

### 7.1 Successful Payment
- **Preconditions**: 
  - Cart has items
  - All required fields filled
- **Action**: Click "Pay Now"
- **Expected**:
  - Form sections hide
  - `#payment-success` becomes visible
  - Shows "Payment Successful!"
  - Shows order number (format: ORD-[timestamp])

### 7.2 Payment with Empty Cart
- **Precondition**: Cart is empty
- **Action**: Click "Pay Now"
- **Expected**: 
  - Alert: "Your cart is empty. Please add items before checkout."
  - Payment not processed

### 7.3 Payment with Invalid Form
- **Precondition**: Cart has items, form incomplete
- **Action**: Click "Pay Now"
- **Expected**:
  - Validation errors shown
  - Payment not processed
  - User remains on checkout page

## 8. End-to-End Test Scenarios

### 8.1 Complete Checkout Flow - Basic
1. Add Wireless Headphones to cart
2. Fill in name: "John Doe"
3. Fill in email: "john@example.com"
4. Fill in address: "123 Main St"
5. Keep Standard Shipping
6. Keep Credit Card
7. Click Pay Now
8. **Expected**: Payment Successful!

### 8.2 Complete Checkout Flow - With Discount
1. Add Smart Watch and Portable Charger
2. Apply discount code "SAVE15"
3. Select Express Shipping
4. Fill all required fields
5. Select PayPal
6. Click Pay Now
7. **Expected**: Payment Successful with correct total

### 8.3 Cart Modification After Discount
1. Add products, apply SAVE15
2. Change quantities
3. **Expected**: Discount percentage remains, amounts recalculate

## Element Reference

| Element | ID/Selector | Purpose |
|---------|-------------|---------|
| Add Product 1 | `#add-product-1` | Add Wireless Headphones |
| Add Product 2 | `#add-product-2` | Add Smart Watch |
| Add Product 3 | `#add-product-3` | Add Portable Charger |
| Discount Input | `#discount-code` | Enter discount code |
| Apply Button | `#apply-discount` | Apply discount |
| Discount Message | `#discount-message` | Success/error message |
| Customer Name | `#customer-name` | Name input field |
| Customer Email | `#customer-email` | Email input field |
| Customer Address | `#customer-address` | Address textarea |
| Standard Shipping | `#shipping-standard` | Shipping radio |
| Express Shipping | `#shipping-express` | Shipping radio |
| Credit Card | `#payment-credit-card` | Payment radio |
| PayPal | `#payment-paypal` | Payment radio |
| Pay Now | `#pay-now` | Submit button |
| Payment Success | `#payment-success` | Success message |
| Subtotal | `#subtotal` | Subtotal display |
| Discount Amount | `#discount-amount` | Discount display |
| Shipping Cost | `#shipping-cost` | Shipping display |
| Grand Total | `#grand-total` | Total display |