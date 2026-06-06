FROM python:3.12-slim

# ── Security: non-root user ───────────────────────────────────────────────────
RUN groupadd -r agent && \
    useradd -r -g agent -d /home/agent -s /sbin/nologin -u 1000 agent && \
    mkdir -p /home/agent && chown agent:agent /home/agent

WORKDIR /app

# ── Dependencies ──────────────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Application code ──────────────────────────────────────────────────────────
COPY --chown=agent:agent . .

# ── Workspace mount point ──────────────────────────────────────────────────────
RUN mkdir -p /workspace && chown agent:agent /workspace

USER agent

HEALTHCHECK --interval=60s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://host.docker.internal:11434/api/tags', timeout=5)" || exit 1

CMD ["python", "main.py"]
