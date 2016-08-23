# Set up joai OMI-PMH provider
jOAI [1] is used to serve content via *OAI-PMH* protocol. 

## Set up server

1. download jOAI [2] or use the attached war file
1. use docker to deploy the application in a tomcat server
 
 ```
 docker run -d -p 8080:8080 -v /home/jj/git/joais/joai/oai.war:/usr/local/tomcat/webapps/oai.war -v /tmp/myvol/:/myvol/ tomcat:latest
 ```
 
The first volume is used to inject the application *war* file, the second one will be used to inject the actual data that should be made available.
 
## Set up service provider

Use a browser to go to:
 ```
 http://0.0.0.0:32772/oai/admin/update_repository_info.do
 ```
Provide basic repository information
 
```
http://0.0.0.0:32772/oai/admin/data-provider.do
```
Set up metadata we use dublin core (*oai_dc*), and define location to */myvol/* (see above). 

## Set up data store

Data put in the */tmp/myvol/* in xml format will be made available through the *OAI-PMH* interface. The files are indexed once a day or reindexing can be triggered manualy through the admin console. An example python programm which takes the data from a graph database and dump it into files. jOAI requires the records to be stored in separate files with id in part of the file name.

 
## References

* [1] http://www.dlese.org/dds/services/joai_software.jsp
* [2] http://sourceforge.net/projects/dlsciences/files/jOAI%20-%20OAI%20Provider_Harvester/


