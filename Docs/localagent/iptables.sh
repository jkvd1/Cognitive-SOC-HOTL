#!/usr/bin/env bash
# iptables.sh — Network-level egress restriction for the localagent container.
# Run ONCE on the Docker host after `docker compose up -d`.
#
# Strategy: Block ALL egress from agent_net bridge, then whitelist:
#   1. localhost:11434 (Ollama)
#   2. api.telegram.org:443

set -euo pipefail

# ── Discover the bridge interface for agent_net ───────────────────────────────
BRIDGE=$(docker network inspect localagent_agent_net \
  --format '{{.Options.com_docker_network_bridge_name}}' 2>/dev/null \
  || docker network inspect localagent_agent_net \
     --format '{{index .Options "com.docker.network.bridge.name"}}' 2>/dev/null \
  || echo "")

if [[ -z "$BRIDGE" ]]; then
  # Fall back: find by subnet
  SUBNET=$(docker network inspect localagent_agent_net --format '{{range .IPAM.Config}}{{.Subnet}}{{end}}')
  BRIDGE=$(ip route | grep "$SUBNET" | awk '{print $3}' | head -1)
fi

if [[ -z "$BRIDGE" ]]; then
  echo "[ERROR] Could not detect agent_net bridge interface. Set BRIDGE manually."
  exit 1
fi

echo "[INFO] Applying iptables rules to bridge: $BRIDGE"

# Resolve Telegram API IP(s)
TELEGRAM_IPS=$(getent ahostsv4 api.telegram.org | awk '{print $1}' | sort -u)

# ── Flush any existing rules for this bridge ─────────────────────────────────
iptables -D FORWARD -i "$BRIDGE" -j DROP 2>/dev/null || true

# ── Allow established/related connections (return traffic) ───────────────────
iptables -I FORWARD 1 -i "$BRIDGE" -m state --state ESTABLISHED,RELATED -j ACCEPT

# ── Allow Ollama on localhost:11434 ──────────────────────────────────────────
iptables -I FORWARD 2 -i "$BRIDGE" -d 127.0.0.1 -p tcp --dport 11434 -j ACCEPT
# host.docker.internal typically resolves to 172.17.0.1 or docker0 IP
HOST_IP=$(ip route | awk '/docker0/ {print $9}' | head -1)
if [[ -n "$HOST_IP" ]]; then
  iptables -I FORWARD 3 -i "$BRIDGE" -d "$HOST_IP" -p tcp --dport 11434 -j ACCEPT
fi

# ── Allow Telegram API ───────────────────────────────────────────────────────
RULE_POS=4
for IP in $TELEGRAM_IPS; do
  echo "[INFO] Allowing api.telegram.org → $IP:443"
  iptables -I FORWARD $RULE_POS -i "$BRIDGE" -d "$IP" -p tcp --dport 443 -j ACCEPT
  RULE_POS=$((RULE_POS + 1))
done

# ── Block everything else from this bridge ───────────────────────────────────
iptables -A FORWARD -i "$BRIDGE" -j DROP

echo "[OK] iptables rules applied. Agent network restricted to Ollama + Telegram only."
echo ""
echo "To verify:"
echo "  docker exec localagent sh -c 'wget -q --spider https://google.com' && echo BREACH || echo BLOCKED"
