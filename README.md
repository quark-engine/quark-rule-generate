# Quark-Rule-Generate Usage

### MongoDB Setup

We store and manage rules with MongoDB, so we need to setup database before generating detection rules for quark engine.

Here are three ways to install MongoDB.
1. Install with Docker
```bash
$ docker pull mongo:4.2
$ docker run -d -p 27017:27017 -v data/db --name mongodb \
      -e MONGO_INITDB_ROOT_USERNAME=root \
      -e MONGO_INITDB_ROOT_PASSWORD=pass \
      mongo:4.2
```

2. Install to local environment
We provide a setup script to install database in your local environment. 
```bash
$ sudo bash scripts/setup_db.sh
```

3. Or you can follow the MongoDB official installation [MongoDB Install](https://docs.mongodb.com/manual/installation/) to setup manually.

### Install Scripts for Rule Generation
```bash
$ git clone https://github.com/quark-engine/quark-rule-generate.git; cd quark-rule-generate/
$ pipenv install --skip-lock
$ pipenv shell
```

### Generate Detection Rules
 
A simple way to generate rules with an APK.
```bash
$ python start.py -a <apk-path>
```

However, the speed of generate progress will be very slow if the APK sample size is large, so we provide an option to generate rules with multiprocessing, here is the example.

> Be Aware it probably will cost a lots of memory.
```bash
$ python start.py -a <apk-path> --multiprocess 3 # Using three processes to work
```

### Export rules to JSON file

Since [Quark-Engine](https://github.com/quark-engine/quark-engine) is using JSON file to analyze APK, here is a way to export rules from database into JSON file.
```bash
$ python start.py -a <apk-path> --export <output-path>
```
