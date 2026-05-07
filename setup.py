from setuptools import setup, find_packages

setup(
    name="hermes-proxy-reply-plugin",
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
            "proxy-reply = plugin:ProxyReplyPlugin",
        ],
        "console_scripts": [
            "hermes-proxy-web = web.app:run",
        ]
    },
    author="Hermes Agent",
    description="智能代理回复系统 - 在微信群聊中自动代替用户回复消息",
    keywords=["hermes", "wechat", "proxy", "auto-reply", "web-panel"],
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