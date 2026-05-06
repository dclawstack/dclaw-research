# Troubleshooting

Common issues and solutions for DClaw Research.

## Quick Diagnostics

```bash
# Check app pods
kubectl get pods -n dclaw-research

# Check logs
kubectl logs -n dclaw-research deployment/dclaw-research-backend

# Check database
kubectl get clusters -n dclaw-research
```

## Sections

- [Common Issues](./common-issues)
- [FAQ](./faq)
