# Item Catalog

## Project Overview

You will develop an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.


## How to Run A Program

### Installation:
* Virtualbox
* Vagrant
* Python

### Setup Enviromnemt
* Download or Clone [Full Stack Nanodegree Virtual Machine](https://github.com/udacity/fullstack-nanodegree-vm).
* Download or Clone [the project](https://github.com/exploit021/Udacity-FNSD-Project2-Item-Catalog)


### Prerequisits for External Autentication
1. Google Authentication
    * You need ClientID and ClientSecret to use Google Authentication.
    * To create keys for your own, please refer a [link](https://developers.google.com/identity/protocols/OAuth2).
```
{"web":
    {
        "client_id":"YOUR_CLIENT_ID_HERE",
        "project_id":"YOUR_PROJECT_ID",
        "auth_uri":"https://accounts.google.com/o/oauth2/auth",
        "token_uri":"https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
        "client_secret":"YOUR_CLIENT_SECRET",
        "redirect_uris":["http://localhost:5000"]
    }
}
```


2. Facebook Authentication
    * You need AppID and AppSecret to use Facebook Authentication and have to run your application on HTTPS.
    * To create key for your own, please refer a [link](https://developers.facebook.com/docs/facebook-login/web).
    * Note: it is required to use HTTPS for Facebook Authentication. If you are test locally, and testing under http://localhost:5000 it will not work. The json file should be formatted like:
```
{
    "web": {
      "app_id": "YOUR_APP_ID",
      "app_secret": "YOUR_APP_SECRET"
    }
  }
```



### Running the program

0. To find more detailed explanation, refer this [link](https://github.com/udacity/fullstack-nanodegree-vm).
1. Open command-prompt or Git Bash and navigate to downloaded Full Stack Nanodegree Virtual Machine folder.
2. Run following command to launch VM.

```$ vagrant up```

2. Once VM started, run following commandd to open and login to SSH.

```$ vagrant ssh```

3. Navigate the folder where `itemcatalog.py` located (e.g. cd /vagrant).
4. Create database by using command below:

```$ python database_setup.py```

5. Seed database by using command below:

```$ python database_seed.py```

6. Run program by using following command depends on version of Python.

```
python itemcatalog.py
python3 itemcatalog.py
```

7. Navigate to http://localhost:5000 from your browser to view the site.

## Style Guide
The PEP8 style guide is an excellent standard to follow.

You can install the `pycodestyle` tool to test this, with `pip install pycodestyle` or `pip3 install pycodestyle` (Python 3).
In order to test, run the following command.

```$ pycodestyle itemcatalog.py```