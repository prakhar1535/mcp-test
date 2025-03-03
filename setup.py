from setuptools import setup, find_packages

setup(
    name="mcp-tool",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyautogui",
        "rich",
        "requests",
        "pillow",
        "pynput",
        "python-xlib",
    ],
    entry_points={
        'console_scripts': [
            'mcp=main:main',
        ],
    },
) 