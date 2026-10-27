from datetime import date
from scripts.progress import load_or_start, is_completed, save
state = load_or_start("b", date(2026,10,27))
print("completed:", is_completed(state))
print("resumed_count:", state.get("resumed_count"))
print("sessies:", state.get("sessies"))
print("competities gedaan:", list((state.get("competitions") or {}).keys()))
save(state)
