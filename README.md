# field-schedule

A scheduling tool for Danish football clubs. It plans training sessions across fields and subfields with Google's CP-SAT solver. It is the scheduling tool behind my bachelor project, [Constraint-based Scheduling in CP-SAT](https://github.com/rohde01/bachelor-project).

## Contents

| Folder | Contents |
| --- | --- |
| `backend/` | FastAPI service with the CP-SAT model in `main.py` and the objectives in `objectives.py` |
| `frontend/` | SvelteKit app on Supabase, deployed to Vercel |

## Run

```bash
cd backend && pip install -r requirements.txt && python server.py
```

```bash
cd frontend && npm install && npm run dev
```

The frontend reads `PUBLIC_API_URL`, `PUBLIC_SUPABASE_URL` and `PUBLIC_SUPABASE_ANON_KEY` from its environment.
