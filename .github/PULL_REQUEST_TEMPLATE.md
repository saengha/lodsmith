## Summary

- New `recipes/<id>.json` or `sets/<id>.json`? (`python -m addon new recipe …` is fine)
- [ ] `id` is a real prop name (not reserved, slur, joke, or `crate2` spam)
- Recipe: `id` matches filename, `target_tris` is `12 ×` parts
- Set: every `items[].recipe` is already shipped
- CREDITS.md line for your handle (same PR)

## Test plan

- [ ] `python -m addon validate`
- [ ] `python -m pytest`
- [ ] (If you have Blender) Build or Build set → Validate

Tag **@saengha**.
