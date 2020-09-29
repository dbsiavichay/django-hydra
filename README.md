=====
Hydra
=====

Hydra is a Django app to build templates easily, and generate site page like django admin.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "hydra" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'hydra',
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('polls/', include('polls.urls')),

3. Run ``python manage.py migrate`` to create the polls migrations.

4. Continue