Ssshare (Simple Secrets Sharing)
===

#### Secrets sharing system

Encrypts a secret, set up a quorum for the disclosure and give its pieces privately to shareholders.
At any point in the future, if enough participants agreed, the secret is rebuilt.

Ssshare it's able to make n-on-m secrets sharings and supports: 
 - [Dyne's FXC web-api & crypto-library](https://github.com/dyne/FXC-webapi)

##### Requirements
 - Code, theoretically, may run on any platform, but compatibility is maily targeted for GNU/Linux
 - Python 3.4
 - Java 1.7 for FXC support 
 

##### Usage
When requirements are satisfied, setup script will install ssshare needed dependencies, and build the FXC-webapi,
using Leiningen, if needed.

```
$ setup.sh [ --help ]
$ ./run.sh
```

##### Tests

Tests are already run as last step of the setup script. Anyway they can be run manually:

```
$ . venv/bin/activate
$ python -m unittest
```

##### What is this ?

A service to manage the sharing and disclosure of any kind of data.
 
May be used:
 - into an IoT network to programmatically set up a real-time secret sharing session with custom policies, parties agree
 to unlock data when certain _real world_ conditions are met 
 - between parties, to keep crypto credentials shared and safe

Assuming a secret policy is a 2-on-3, the diagram is the following:

![Flow diagram](https://raw.githubusercontent.com/gdassori/ssshare/master/resources/secret_split_and_recovery.png)

##### How ?

Via easy-to-use HTTP API, for computers, and a web app, for humans (or viceversa...).
API documentation, still immature, will follow.
