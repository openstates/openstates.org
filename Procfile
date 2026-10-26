db: docker-compose --profile db up db
backend: npm run start
web: DATABASE_URL=postgis://openstates:openstates@localhost:5405/openstatesorg uv run ./manage.py runserver
