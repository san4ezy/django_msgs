import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django_msgs",
    version="1.7.5",
    author="Alexander Yudkin",
    author_email="san4ezy@gmail.com",
    description="Emails and SMSs managing framework for Django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/san4ezy/django_msgs",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
    install_requires=[
        'django_json_widget',
    ],
    extras_require={
        'sendgrid': ['sendgrid>=6.0.0'],
        'twilio': ['twilio>=7.0.0'],
        # 'sendinblue': ['sib-api-v3-sdk>=7.0.0'],
        'plivo': ['plivo>=4.0.0'],
        # ... other providers
    },
)
