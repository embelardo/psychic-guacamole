#!/usr/bin/bash

echo; echo "Install ius-release repo"
yum install -y https://centos7.iuscommunity.org/ius-release.rpm

#Skip full update
#sudo yum update -y

echo; echo "Install python3.6"
yum install -y python36u python36u-libs python36u-devel python36u-pip

echo; echo "Test installed python3.6 by printing version"
python3.6 -V

echo; echo "Install pip3"
pip3.6 install --upgrade pip

echo; echo "Install ipython3"
pip3.6 install ipython

echo; echo "Test installed ipython3 by printing version"
ipython3 -V

echo; echo "Install untangle"
# untangle parses an XML document and returns a Python object which makes it easy to access the data you want.
pip3.6 install untangle
