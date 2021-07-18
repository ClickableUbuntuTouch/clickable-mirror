#!/bin/bash

echo "-----BEGIN PGP PUBLIC KEY BLOCK-----" > pub.gpg
echo $GPG_PUBLIC | tr " " "\n" >> pub.gpg
echo "-----END PGP PUBLIC KEY BLOCK-----" >> pub.gpg
gpg --import pub.gpg
rm pub.gpg

echo "-----BEGIN PGP PRIVATE KEY BLOCK-----" > pri.gpg
echo $GPG_PRIVATE | tr " " "\n" >> pri.gpg
echo "-----END PGP PRIVATE KEY BLOCK-----" >> pri.gpg

gpg --allow-secret-key-import --import pri.gpg
rm pri.gpg
