from setuptools import setup, find_packages

setup(
    name="hermes-wechat-reply-delegation-plugin",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyyaml",
        "pytz",
        "flask",
        "flask-login",
        "flask-cors",
    ],
    entry_points={
        "hermes.plugins": [
            "wechat-reply-delegation = plugin:ProxyReplyPlugin",
        ],
        "console_scripts": [
            "hermes-wechat-reply-web = web.app:run",
        ]
    },
    author="Hermes Agent",
    description="WeChat Group Reply Delegation Plugin - Automatically reply to WeChat group messages on behalf of users",
    keywords=["hermes", "wechat", "reply", "delegation", "auto-reply", "group-chat"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
)