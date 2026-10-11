# JonesH/hello

The first `jonesh` tenant app (astrocloud roadmap Stage 3.8). A minimal FastAPI
service that proves the platform wiring end to end:

- **postgres** - a `visits` counter incremented on each page load (shared `nuk-postgres`),
- **redis** - a `hello:hits` counter (shared `nuk-redis`),
- served at **https://hello.jonesh.de**.

It reads `DATABASE_URL` / `REDIS_URL` from the environment; nuk injects them via the
per-app creds env-file it attaches to the `web` ingress service (`spec.databases` in
`JonesH/infra/deployments/hello.yml`). Nothing is hardcoded.

Deployed by the convergence loop from `JonesH/infra`; the image is built on the app
host by `docker compose up -d`.
