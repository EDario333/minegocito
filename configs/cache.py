''' 
Next one for use with memcached
https://docs.djangoproject.com/en/2.2/topics/cache/#memcached

Please be sure that memcached is installed: apt install memcached
Also configure the service at /etc/memcached.conf
'''

CACHES = {
	'default': {
		'BACKEND':	'django.core.cache.backends.memcached.MemcachedCache',
		#'LOCATION': 'unix:/var/run/memcached.sock:0',
		'LOCATION': '127.0.0.1:11211',
	}
}

''' 
Next one for use with filesystem caching
https://docs.djangoproject.com/en/2.2/topics/cache/#filesystem-caching
'''
'''
CACHES = {
	'default': {
		'BACKEND':	'django.core.cache.backends.filebased.FileBasedCache',
		#'LOCATION': 'unix:/var/run/memcached.sock:0',
		'LOCATION': '/var/tmp/django_cache',
	}
}
'''

''' 
Next one for use with Redis.
Please be sure that Redis is installed: apt install redis
Also ensure that redis server is running: redis-cli ping

https://realpython.com/caching-in-django-with-redis/
'''
'''
CACHES = {
	'default': {
		'BACKEND': 'django_redis.cache.RedisCache',
		'LOCATION': 'redis://127.0.0.1:6379/1',
		'OPTIONS': {
			'CLIENT_CLASS': 'django_redis.client.DefaultClient'
		},
		'KEY_PREFIX': 'minegocito'
	}
}
'''
CACHE_MIDDLEWARE_ALIAS='default'
CACHE_MIDDLEWARE_SECONDS=600
CACHE_MIDDLEWARE_KEY_PREFIX='minegocito'