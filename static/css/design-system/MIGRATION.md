# Design System Migration Guide

This guide provides instructions on how to migrate from the legacy CSS to the new design system components while maintaining backward compatibility.

## Table of Contents
1. [Overview](#overview)
2. [Design Tokens](#design-tokens)
3. [Components](#components)
4. [Migrating Existing Code](#migrating-existing-code)

## Overview

The new design system architecture provides:
- Centralized design tokens
- Reusable components
- Better maintainability
- Consistent styling

## Design Tokens

### Colors
Old | New
--- | ---
`--white` | `--color-white`
`--black` | `--color-black` 
`--burnt-orange` | `--color-brand-primary`
`--burnt-orange-light` | `--color-brand-primary-light`
`--burnt-orange-dark` | `--color-brand-primary-dark`
`--text-dark` | `--color-text-primary`
`--text-medium` | `--color-text-secondary`
`--text-light` | `--color-text-tertiary`

### Typography
Old | New
--- | ---
`'Plus Jakarta Sans', sans-serif` | `var(--font-family-primary)`
`'Space Grotesk', sans-serif` | `var(--font-family-display)`

### Spacing
Old | New
--- | ---
`--spacing-unit` | Same, but use scale: `--spacing-sm`, `--spacing-md`, etc.
`1rem`, `2rem` | `var(--spacing-md)`, `var(--spacing-xl)`

### Border Radius
Old | New
--- | ---
`--border-radius-sm` | `--radius-sm`
`--border-radius-md` | `--radius-md`
`--border-radius-lg` | `--radius-lg`

## Components

### Buttons
Old | New
--- | ---
`.connect-btn` | `.btn.btn--primary`
`.visit-button` | `.btn.btn--secondary`
`.add-to-cart` | `.btn.btn--primary`

### Cards
Old | New
--- | ---
`.offering-items` | `.card`
`.product-card` | `.card.card--interactive`

## Migrating Existing Code

### Step 1: Use Design Tokens

Replace hard-coded values with design tokens:

```css
/* Before */
.element {
  padding: 1rem;
  color: #2C3E50;
  border-radius: 12px;
}

/* After */
.element {
  padding: var(--spacing-md);
  color: var(--color-text-primary);
  border-radius: var(--radius-sm);
}
```

### Step 2: Use Component Classes

For new components, use the design system classes:

```html
<!-- Before -->
<a href="#" class="connect-btn">Connect with me</a>

<!-- After -->
<a href="#" class="btn btn--primary">Connect with me</a>
```

### Step 3: Gradual Migration

For existing pages, you can gradually migrate by:

1. First, ensure the legacy variables are mapped to the new tokens (already done in base.css)
2. Update CSS files to use the new tokens
3. Replace components one at a time

## Maintaining Backward Compatibility

The system is designed to maintain backward compatibility:

1. Legacy variable names are preserved but reference the new tokens
2. Existing component classes continue to work
3. New components can be used alongside existing ones

## Best Practices

1. Always use design tokens for new code
2. Follow the BEM naming convention for new components
3. Keep components single-responsibility
4. Use responsive design tokens for better mobile support 

## Important Note: Temporary Rollback

The design system implementation has been temporarily rolled back to direct CSS values to fix frontend issues. This approach ensures all styles work correctly while the design system is being integrated.

### Current State

1. **Direct CSS Values**: All components currently use direct CSS values (like `#D35400` instead of `var(--color-brand-primary)`)
2. **Original Class Names**: All original class names are preserved
3. **Component Structure**: The components are organized in the design system structure but use direct values

### Next Steps for Full Integration

1. Gradually reintroduce CSS variables after fixing the import order issues
2. Ensure all components use the proper variable references
3. Implement proper token resolution for nested variables

Before proceeding with further integration:
- Test thoroughly in all browsers
- Validate layout and responsiveness
- Ensure transitions and animations work as expected 