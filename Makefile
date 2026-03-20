full-up:
	docker compose -f docker-compose_full.yml up

full-down:
	docker compose -f docker-compose_full.yml down -v

grafana-up:
	docker compose -f docker-compose_grafana.yml up

grafana-down:
	docker compose -f docker-compose_grafana.yml down -v