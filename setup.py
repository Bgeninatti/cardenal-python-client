from setuptools import setup

setup(
    name='CardenalGenerator',
    version='0.2.0',
    description='Libreria de Python que implementa un cliente para el bot de notificaciones Cardenal',
    author='Bruno Geninatti',
    author_email='bruno@teknotrol.com',
    packages=['CardenalGenerator', ],
    test_suite='nose.collector',
    install_requires=['pyzmq', 'nose'],
)
