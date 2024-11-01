Last Update: Oct 25 2024

# Overview
This repository contains forecasting and research tools built with Python and Streamlit. The project aims to assist users in making predictions, conducting research, and analyzing data related to hard to answer questions (especially those from Metaculus). Find the demo website here: https://mokoresearch.streamlit.app/

Here are the key components and features of the project:
- General Forecaster that integrates with the Metaculus AI benchmarking competition
- Historical Base Rate Researcher
- Niche List Researcher
- Fermi Estimator
- Key Factors Analysis

# Getting Set Up

## Environment Variables
The environment variables from ```.env.template``` are needed to run. Copy this template as ```.env``` and fill it in. Talk to the project owner to get the correct values for some of the more project specific variables.

## Docker Dev Container
To get your development environment up and running, you need to have Docker Engine installed and running. Once you do, you can use the VSCode dev container pop-up to automatically set up everything for you

### Install Docker
For Windows and Mac, you will download Docker Desktop. For Linux, you will download Docker Engine. (NOTE: These instructions might be outdated).

First download and setup Docker Engine using the instructions at the link below for your OS:
 * Windows: [windows-install](https://docs.docker.com/desktop/install/windows-install/)
 * Mac: [mac-install](mac-install)
 * Linux: [install](https://docs.docker.com/engine/install/)
    * Note: DO NOT install Docker Desktop for Linux, rather, select your Linux distribution on the left sidebar and follow the distribution specific instructions for Docker engine. Docker Desktop runs with a different environment in Linux. (TODO: Check if this restriction still applies)
    * Remember to follow the post-installation steps for Linux: [linux-postinstall](https://docs.docker.com/engine/install/linux-postinstall/)


### Starting the container
Once Docker is installed, when you open up the project folder in VSCode, you will see a pop up noting that you have a setup for dev containers, and asking if you would like to open the folder in a container. You will want to click "open in container". This will automatically set up everything you need and bring you into the container. If the docker process times out in the middle of installing python packages you can run the postinstall.sh manually. You also may need to have the VSCode Docker extension and/or devcontainer extension downloaded

You may need to reinstall some vscode extensions in the dev environment if you are opening it for the first time, but this should only be for the first time running it.

Some extensions are installed automatically (e.g. linting). You may need to reload the window after all of these extensions are installed.

### Managing Docker
There are many ways to manager Docker containers, but generally if you download the vscode docker extension, you will be able to stop/start/remove all containers and images.


### Alternatives to Docker
If you choose not to run docker, use a python virtual environment so these packages don't conflict with local packages. To set this up run

```
python -m venv .venv
```

If you use a virtual environment, install python packages and their dependencies to the virtual environment via the command

```
pip install --require-virtualenv -r requirements.txt
```

## Running the Front End
You can run any front end folder in the front_end directory by executing `streamlit run front_end/[site_file_name]/Home.py`. This will start a development server for you that you can run.


# Testing
This repository uses pytest and pytest-xdist. xdist spreads out all the tests between multiple threads that are each run on a separate CPU. Currently its setup to create a thread per CPU. Configuration for this is in `pytest.ini`. The tests are gathered afresh from each thread, so any initialization done in imports, globals, or class variables are done for each thread. Additionally, global state is not reset between tests on the same thread. When making tests, assume unknown values for globals and especially class variables (though try to avoid using these at all).
