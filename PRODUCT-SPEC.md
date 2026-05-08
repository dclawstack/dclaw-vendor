# PRODUCT-SPEC: Vendor

## Overview

**App Name:** Vendor
**Domain:** Supplier & Purchase Order Management
**Target User:** Procurement teams, operations managers

## Core Entities

### Vendor
```
Vendor
├── id: UUID (PK)
├── name: str (required)
├── contact_name: str (optional)
├── email: str (optional)
├── phone: str (optional)
├── address: str (optional)
├── payment_terms: str (optional) — e.g. "Net 30", "Net 60"
├── status: enum ["active", "inactive", "blacklisted"] (default: "active")
├── created_at: datetime
└── updated_at: datetime
```

### PurchaseOrder
```
PurchaseOrder
├── id: UUID (PK)
├── vendor_id: UUID (FK → Vendor, ondelete=SET NULL)
├── status: enum ["draft", "sent", "partial", "received", "cancelled"] (default: "draft")
├── total: float (required, default 0)
├── expected_delivery: date (optional)
├── notes: str (optional)
├── created_at: datetime
└── updated_at: datetime
```

### POLineItem
```
POLineItem
├── id: UUID (PK)
├── po_id: UUID (FK → PurchaseOrder, ondelete=CASCADE)
├── product_name: str (required)
├── description: str (optional)
├── quantity: int (required, default 1)
├── unit_price: float (required, default 0)
├── received_qty: int (default 0)
├── created_at: datetime
└── updated_at: datetime
```

## User Stories / Screens

### Screen 1: Dashboard
- Summary cards: active vendors, open POs, POs pending delivery, total spend
- Recent POs feed
- Vendors by status chart
- Quick actions (add vendor, create PO)

### Screen 2: Vendors
- Table view with pagination, search by name/email
- Status filter (active/inactive/blacklisted)
- "Add Vendor" modal/form

### Screen 3: Vendor Detail
- Vendor info card with edit/delete
- Related POs list
- Add PO button

### Screen 4: Purchase Orders
- Table view with pagination, search by vendor
- Status filter (draft/sent/partial/received/cancelled)
- "Add PO" form with vendor dropdown and line items

### Screen 5: PO Detail
- PO info with edit/delete
- Line items table with receive tracking
- Status update buttons (send → partial → received)
- Total calculation

## API Endpoints

- `GET /api/v1/vendors` — list vendors
- `POST /api/v1/vendors` — create vendor
- `GET /api/v1/vendors/{id}` — get vendor
- `PATCH /api/v1/vendors/{id}` — update vendor
- `DELETE /api/v1/vendors/{id}` — delete vendor

- `GET /api/v1/purchase-orders` — list POs
- `POST /api/v1/purchase-orders` — create PO
- `GET /api/v1/purchase-orders/{id}` — get PO
- `PATCH /api/v1/purchase-orders/{id}` — update PO
- `DELETE /api/v1/purchase-orders/{id}` — delete PO

- `GET /api/v1/po-line-items` — list line items
- `POST /api/v1/po-line-items` — create line item
- `PATCH /api/v1/po-line-items/{id}` — update line item
- `DELETE /api/v1/po-line-items/{id}` — delete line item
