### These commands are run after the docker image for the dev container is built ###

# Install pipx (https://pipx.pypa.io/stable/installation/)
sudo apt update
sudo apt install pipx

# Install poetry using pipx (https://python-poetry.org/docs/#installation)
pipx install poetry

poetry install
pre-commit install
