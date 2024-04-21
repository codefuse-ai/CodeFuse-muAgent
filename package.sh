#!/bin/bash


# rm -rf build coagent.egg-info muagent.egg-info dist

# python setup.py sdist bdist_wheel

# pip uninstall coagent -y
# pip install dist/coagent-0.0.101-py3-none-any.whl

# rm -rf build coagent.egg-info muagent.egg-info dist


rm -rf build coagent.egg-info muagent.egg-info dist

python setup_test.py sdist bdist_wheel

pip uninstall muagent -y
pip uninstall coagent -y
pip install dist/muagent-0.0.101-py3-none-any.whl

rm -rf build coagent.egg-info muagent.egg-info dist
