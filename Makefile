DC = docker compose
STORAGES_FILE = docker_compose/storages.yaml
APP_FILE = docker_compose/app.yaml
EXEC = docker exec -it
DB_CONTAINER = example-db
APP_CONTAINER = main-app
LOGS = docker logs
PYTHON_MANEGE = python manage.py
ENV_FILE = --env-file .env


.PHONY: storages
storages:
	${DC} -f ${STORAGES_FILE} ${ENV_FILE} up -d


.PHONY: storages-logs
storages-logs:
	${LOGS} ${DB_CONTAINER} -f


.PHONY: storages-down
storages-down:
	${DC} -f ${STORAGES_FILE} down



.PHONY: app
app:
	${DC} -f ${STORAGES_FILE} -f ${APP_FILE} ${ENV_FILE} up -d

.PHONY: app-logs
app-logs:
	${LOGS} ${APP_CONTAINER} -f


.PHONY: app-down
app-down:
	${DC} -f ${STORAGES_FILE} -f ${APP_FILE} down

.PHONY: restart
restart:
	${DC} -f ${STORAGES_FILE} -f ${APP_FILE} down && ${DC} -f ${STORAGES_FILE} -f ${APP_FILE} ${ENV_FILE} up --build -d


.PHONY: migrations
migrations:
	${EXEC} ${APP_CONTAINER} ${PYTHON_MANEGE} makemigrations


.PHONY: migrate
migrate:
	${EXEC} ${APP_CONTAINER} ${PYTHON_MANEGE} migrate


.PHONY: superuser
superuser:
	${EXEC} ${APP_CONTAINER} ${PYTHON_MANEGE} createsuperuser


.PHONY: collectstatic
collectstatic:
	${EXEC} ${APP_CONTAINER} ${PYTHON_MANEGE} collectstatic