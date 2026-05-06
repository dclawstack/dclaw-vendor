# Troubleshooting

Common issues and solutions for DClaw Vendor.

## Quick Diagnostics

```bash
# Check app pods
kubectl get pods -n dclaw-vendor

# Check logs
kubectl logs -n dclaw-vendor deployment/dclaw-vendor-backend

# Check database
kubectl get clusters -n dclaw-vendor
```

## Sections

- [Common Issues](./common-issues)
- [FAQ](./faq)
