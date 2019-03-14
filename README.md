This is a simple flask app that fetches and display user time duration per project.
---
###Requirements
* docker must be installed
* the project (git cloned or download)

###Steps
1. cd to the root dir of the project
2. open `settings.py`, make sure to fill app this
    `HUBSTAFF_APP_TOKEN=''`
    `HUBSTAFF_EMAIL=''`
    `HUBSTAFF_PASSWORD=''`
3. run `docker build --tag=<image-name> .`. Image name can be whatever you e.g `hubstaff`.
4. run `docker run --name=<container-name> -p <host-port>:5000 <image-name>`
5. you can now access `0.0.0.0:<host-port>`
