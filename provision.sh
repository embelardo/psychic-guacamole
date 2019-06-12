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
# Untangle parses an XML document and returns a Python object which makes it easy
# to access the data you want.
pip3.6 install "untangle==1.1.1"

echo; echo "Install pyzotero"
# Pyzotero is a Python wrapper for the Zotero API (v3).
pip3.6 install "pyzotero==1.4.1"

echo; echo "Install zotero-cli"
# Zotero-cli is a simple command-line interface for the Zotero API.
pip3.6 install zotero-cli

echo; echo "Install pandoc"
# Pandoc is a Haskell library for converting from one markup format to another,
# and a command-line tool that uses this library.
# Required by zotero-cli
yum install -y pandoc

echo; echo "Install mlocate"
# mlocate is a locate/updatedb implementation. It keeps a database of all
# existing files and allows you to lookup files by name.
yum install -y mlocate
updatedb

echo; echo "Install patch"
# The patch program applies diff files to originals.
# The diff command is used to compare an original to a changed file.
yum install -y patch

echo; echo "Patch pyzotero for content-type and charset of uploaded .patch.txt and .xml files"
# For .patch.txt: content-type = 'text/plain', and charset = 'iso-8859-1'
# For .xml      : content-type = 'text/plain', and charset = 'utf-8'
patch -p0 < /vagrant/zotero_patch_contenttype_charset.patch -d /
