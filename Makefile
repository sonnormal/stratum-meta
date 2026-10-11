.PHONY: e2e-up e2e-verify e2e-down e2e-logs uat-up uat-verify uat-down uat-logs help

help:
	@echo "Stratum Developer & Tier 3 E2E Control Commands:"
	@echo "  make e2e-up      - Start Ollama daemon & multi-container stack until healthy"
	@echo "  make e2e-verify  - Execute automated end-to-end Tier 3 verification & display results"
	@echo "  make e2e-down    - Stop and tear down E2E containers"
	@echo "  make e2e-logs    - Follow live container logs"

e2e-up:
	@./scripts/e2e-up.sh

e2e-verify:
	@./scripts/e2e-verify.sh

e2e-down:
	@./scripts/e2e-down.sh

e2e-logs:
	@docker compose -f deploy/docker-compose.yml logs -f

# Aliases for backward compatibility
uat-up: e2e-up
uat-verify: e2e-verify
uat-down: e2e-down
uat-logs: e2e-logs
