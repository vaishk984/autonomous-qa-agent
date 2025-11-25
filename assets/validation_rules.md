# Form Validation Rules and Error Handling

## Overview
This document defines all validation rules for the E-Shop checkout form, including field requirements, validation patterns, and error message specifications.

## Required Fields

### 1. Customer Name (customer-name)
- **Field Type:** Text input
- **Required:** Yes
- **Validation Rule:** Must not be empty or whitespace-only
- **Error Message:** "Please enter your full name"
- **Error Element ID:** name-error
- **Validation Trigger:** On form submission (Pay Now click)
- **Error Clear Trigger:** On user input

### 2. Customer Email (customer-email)
- **Field Type:** Email input
- **Required:** Yes
- **Validation Rules:**
  - Must not be empty
  - Must match email format pattern: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`
  - Must contain @ symbol
  - Must have domain part after @
- **Error Message:** "Please enter a valid email address"
- **Error Element ID:** email-error
- **Valid Examples:** john@example.com, user.name@domain.co.uk
- **Invalid Examples:** john, john@, @example.com, john@example

### 3. Customer Address (customer-address)
- **Field Type:** Textarea
- **Required:** Yes
- **Validation Rule:** Must not be empty or whitespace-only
- **Error Message:** "Please enter your shipping address"
- **Error Element ID:** address-error

## Optional Fields

### 4. Customer Phone (customer-phone)
- **Field Type:** Text input
- **Required:** No
- **Validation Rule:** None (optional field)
- **Error Element ID:** phone-error (reserved for future use)

## Visual Error Indicators

### Input Field Error State
```css
.input-error {
    border-color: #f44336 !important;
}
```

### Error Message Styling
```css
.error-message {
    color: #f44336;
    font-size: 0.85em;
    margin-top: 5px;
    display: none;  /* Hidden by default */
}
```

## Validation Flow

### Step 1: Form Submission Triggered
- User clicks "Pay Now" button
- validateForm() function is called

### Step 2: Cart Validation
- Check if cart has items
- If empty: Show alert "Your cart is empty. Please add items before checkout."
- If not empty: Proceed to field validation

### Step 3: Field Validation Sequence
1. Validate Name field
2. Validate Email field
3. Validate Address field
4. Return overall validation status

### Step 4: Validation Actions per Field
For each field:
1. Get field value using `.value.trim()`
2. Check against validation rule
3. If invalid:
   - Add `input-error` class to input element
   - Set error message `display: block`
   - Set isValid = false
4. If valid:
   - Remove `input-error` class
   - Set error message `display: none`

### Step 5: Final Action
- If all validations pass: Process payment
- If any validation fails: Stop submission, keep focus on form

## Error Message Behavior

### Display Conditions
- Error messages are ONLY shown after user attempts to submit
- Multiple errors can be displayed simultaneously
- Errors remain visible until user corrects the field

### Clear Conditions
Error state is cleared when:
- User starts typing in the field (input event)
- Both the red border AND error message are removed

### Error Clear Code Pattern
```javascript
input.addEventListener('input', function() {
    this.classList.remove('input-error');
    const errorEl = this.nextElementSibling;
    if (errorEl && errorEl.classList.contains('error-message')) {
        errorEl.style.display = 'none';
    }
});
```

## Cart-Related Validations

### Empty Cart Check
- **Trigger:** Pay Now button click
- **Condition:** cart.length === 0
- **Action:** Alert message, no form validation performed
- **Message:** "Your cart is empty. Please add items before checkout."

### Discount Code on Empty Cart
- **Trigger:** Apply discount button click
- **Condition:** cart.length === 0
- **Action:** Show error in discount message area
- **Message:** "Please add items to cart first"

## Radio Button Validation

### Shipping Method
- **Field Name:** shipping_method
- **Required:** Yes (one must be selected)
- **Default:** Standard shipping (pre-selected)
- **Options:** standard, express
- **Validation:** Not explicitly validated (always has default)

### Payment Method
- **Field Name:** payment_method
- **Required:** Yes (one must be selected)
- **Default:** Credit Card (pre-selected)
- **Options:** credit_card, paypal
- **Validation:** Not explicitly validated (always has default)

## Test Scenarios for Validation

### Positive Test Cases
1. All required fields filled with valid data → Payment proceeds
2. Valid email formats accepted → No error shown
3. Error clears on user input → Error message disappears

### Negative Test Cases
1. Empty name field → "Please enter your full name"
2. Empty email field → "Please enter a valid email address"
3. Invalid email format → "Please enter a valid email address"
4. Empty address field → "Please enter your shipping address"
5. Empty cart with Pay Now → Alert about empty cart
6. All fields empty → All three error messages shown

### Edge Cases
1. Whitespace-only name → Should fail validation
2. Whitespace-only address → Should fail validation
3. Email without domain extension → Should fail
4. Multiple @ symbols in email → Should fail