# Exploration of PFB
Explore PFB (portable bioinformatics format)

https://github.com/uc-cdis/pypfb

# Setup for Jupyter Notebook

```shell
$ git clone git@github.com:kids-first/notebooks.git
$ cd notebooks/nsingh/kf-lib-pfb_exporter
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ pip install -r explore-requirements.txt
$ jupyter
```

# Background

## What is an Avro File?
A binary compressed file with a schema and data in it.

## Avro Basics

### Avro File
The writer takes in a schema (JSON file) and the data which conforms to that schema, and writes it to an avro file. The schema gets written first, then the data.

### Write Avro
The avro schema is pretty simple. Its a JSON file. It has entities, their attributes, and the types of those attributes. You can represent primitive types and complex types in order to represent the schema for complicated nested JSON structures. Read more about [avro](https://avro.apache.org/docs/current/spec.html).

### Read Avro
The reader doesn't need the schema since its embedded in the data. The reader reads in and parses the avro file to JSON.

## Vanilla Avro vs PFB
Let's say a client receives an avro file. It reads in the avro data. Now a client has the avro schema and all of the data that conforms to that schema in a big JSON blob. It can do what it wants. Maybe it wants to construct some data input forms. To do this it has everything it needs since the schema has all of the entities, attributes, and types for those attributes defined.

Now what happens if the client wants to reconstruct a relational database from the data? How does it know what tables to create, and what the relationships are between those tables? Which relationships are required vs not?

This is where PFB comes in. It has defined a specific avro schema which is suitable for packaging up relational data so that it can be exchanged among clients and then used to reconstruct a relational database.

## Apache Avro

- Don't use this
- Apache's python avro package is super slow because its written in pure Python
- Also the setup.py is missing pycodestyle dependency pypy avro package
can't find StringIO module. I think you need the snappy codec package for it to work.

## Fast Avro

- pypfb uses this package
- Written in cpython so its way faster than Apache's Python package
- Doesn't support schema hashing or parsing into canonical form
(needed for diffing two schemas)

## Python pypfb package

- The CLI is very slow
- Needs to be cleaned up and refactored - code is difficult to follow and
there are large commented sections
