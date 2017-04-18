# ckanext-yammer
This extension provides an simple interface for integrating yammer with CKAN.

Works for ckan>=2.5

## Installation

Use `pip` to install this plugin.

underneath the synced_folders/src directory, run:

```
pip install -e 'git+https://github.com/merkelct/ckanext-yammer.git#egg=ckanext-yammer'
```

## Configuration

Make sure to add `yammerid` in your config file, using your yammer client id:

```
{
    "yammerid":"BJsO334heTOKEN4sDF"
}
```


## Helper Functions

custom helpers available to the templates

```
get_yammer_client_id() - returns the yammer client id (the config object, in the ini file)
yammer_config(yammer_user_id) - returns the yammer configuration for the current user

```

all helpers will be available as h.<helper name>(<vars>)


##Usage

Before you can post to yammer, it must be configured at the org level.

Organization/yammer_config/<your organization>

1. Hit the sign in with yammer button
2. Select which yammer groups you'd like to notify
3. Select any combination of create, update, and delete *
4. Hit update config and you will receive a flash notification if it succeeded or failed


*Create will tell you when a dataset has been created, Update when a dataset has been modified, and delete when a
Dataset has been removed)


Dependencies
------------

* yampy
