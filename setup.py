import setuptools

setup_params = dict(
    name="pmx-game",
    version="0.0.1",
    packages=setuptools.find_packages(),
    entry_points=dict(
        pmxbot_handlers = [
            'pmxbot Text Adventure = pmx_game',
        ]
    ),
    install_requires=[],
    description="IRC text adventure game plugin for pmxbot",
    author="Michael McHugh (mmchugh)",
    author_email="mmchugh@gmail.com",
    maintainer = 'mmchugh@gmail.com',
    maintainer_email = 'mmchugh@gmail.com',
    url = 'http://github.com/mmchugh/pmx-game',
    tests_require=[
        'pytest',
        'pmxbot',
    ],
    setup_requires=[
        'pytest-runner',
    ],
)

if __name__ == '__main__':
    setuptools.setup(**setup_params)
