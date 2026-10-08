.PHONY: uat-up uat-verify uat-down uat-logs help

help:
	@echo "Stratum Developer & UAT Control Commands:"
	@echo "  make uat-up      - Start Ollama daemon & multi-container stack until healthy"
	@echo "  make uat-verify  - Execute automated end-to-end UAT verification & display results"
	@echo "  make uat-down    - Stop and tear down UAT containers"
	@echo "  make uat-logs    - Follow live container logs"

uat-up:
	@./scripts/uat-up.sh

uat-verify:
	@./scripts/uat-verify.sh

uat-down:
	@./scripts/uat-down.sh

uat-logs:
	@docker compose -f deploy/docker-compose.yml logs -f
