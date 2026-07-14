mig:
	python manage.py makemigrations
	python manage.py migrate
make_l:
	django-admin makemessages -l ru
	django-admin makemessages -l uz
	django-admin makemessages -l uz_CYRL

make_cop:
	django-admin compilemessages