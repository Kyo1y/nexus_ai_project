# Running ChatQuote in Docker

## Assumptions in this document

This doc assumes that the application is being built as `pennmutual/chatquote`, so any references to that should be changed if you are not using this Docker image tag for your builds.

This document also assumes you are running a Mac.  If you are using a Windows machine, you will need to know how to do things the Windows way that corresponds to what has been documented here.

## Install Docker

You will need to install a local version of Docker on your machine.  It should not require any special configuration.

## Download this repo!

Let's assume you did this already and you aren't just reading this on BitBucket.

## Build the docker images

Before you can run anything you will need to build the source into a Docker image.  The `Dockerfile` has the build commands needed to do that, and you force the compile by running the following from a shell prompt:

    docker build -t pennmutual/chatquote --target server .

You can also just run the `./docker_build` command that is in the root folder of the project.

You will see the image listed in your Docker Dashboard once the build is complete.  With caching disabled (or an initial build), it will probably take at least 2.5 minutes to complete.

## You will need certificates!

You are going to need a set of personal certificates in order to have your locally running copy of the application connect with the Mailer Service.  In model office and production, those certs will be supplied to the container, but for running locally, you need your own.

**They are not to be included in the application source code.**

1) Contact the ETS group to have them issue a personal cert for you.  Ask for it to be provided in a PKCS12 format, and with a `.p12` file extension.  
2) Also ask for a copy of the `PML-CA_Bundle.pem` file, or get one from a teammate.  That file is the same for all people, so you can get it from any number of PML sources.

Once you have the `p12` cert, you will have to extract out the certificate and key files from it using `openssl`.  Get that installed on your machine if you don't have it already.

Now use the included `./extractfromp12` script to get your files from the `.p12` you received.  Assuming your file was called `John Doe.p12` and the password ETS provided was `iLikePie`, then you would execute the following command:

    ./extractfromp12 "John Doe" "iLikePie"

You would then end up with two new files: `John Doe.pem` (your certificate) and `John Doe.key` (your private key).

Next, create a `certs` folder in your home folder.  For example, certs on my machine can be found in `/Users/moryl/certs`.  Take the two files you just created, your `.p12` file, and the `PML-CA_Bundle.pem` file and move them all into the ~/certs folder you created.

You will next need to generate Base64 encoded versions of your `.pem` and `.key` files.  Those will be needed when you configure your environment, in the next section.

Assuming, again, that your name and that of your files is "John Doe", you would generate these values with the following commands:

    base64 "John Doe.pem"
    base64 "John Doe.key"

Each of these will generate a very long string.  The string generated with your `.pem` file will be used as `TLS_CERT_BASE64` value in the next step, while the one generated from your `.key` file will be used as the `TLS_KEY_BASE64` value.

## Configuring your environment variables

In order to run the application locally, you will need to have a minimum set of environment variables defined.  Those environment variables should be defined in a file called `.env`, and that file **should not be checked into Git**.  Here's an example:

    OAUTH_CLIENT_SECRET="##ChatQuote's OAuth password##"
    SERVER_PORT=5000
    TLS_CA_BUNDLE=/##Path to##/PML-CA_Bundle.pem
    TLS_CERT_BASE64=##your base64 encoded certificate##
    TLS_KEY_BASE64=##your base64 encoded key##
    NODE_ENV=localhost

Anything shown wrapped in ##something## is not a real value.  You should put the real value in there instead.  For the OAuth client secret, check with your teammates.  If they don't have it, check with Michael Oryl or John Russella and ask for the Model Office OAuth client password for your application.

The `TLS_CERT_BASE64` and `TLS_KEY_BASE64` values come from the previous step.

The value used for the `TLS_CA_BUNDLE` depends on where you placed the bundle file.  It should not be checked into code.

## Run the application locally

In order to get the app running, with its MongoDB dependency, you need to start up the application system with the `docker-compose` command that is installed with Docker.

The config for the application is in the `docker-compose.yml` file.

To start the application based on that config, be in the same folder as the YAML file and issue the following command:

    docker-compose up

This will start up NodeJS running ChatQuote, the Webpack dev server (for React), and a built-in version of MongoDB (with no security) in the virtual machine all together.  This will allow ChatQuote to start self-contained.  Otherwise you'd need to specify an external Mongo database (in the `MONGO_URI` env var) and have a username and password setup ahead of time (or at least run Mongo locally), and you'd need to run both the Node.js server and the Webpack server.

Also, note that the above command is the same as the following:

     docker compose -f docker-compose.yml -f docker-compose.override.yml up

By default, `docker-compose` reads the `docker-compose.yml` files **as well as** the default override file `docker-compose.override.yml`.  It is that override file that has the configuration details needed for running in the local environment using your file system for the source instead of using a Docker image.

You can run the simpler `./dcu` command instead of typing the longer docker-compose command above.

**Note that this configuration uses the source in your own project folder, not in the Docker image itself.  The `docker-compose.override.yml` takes care of that by mapping the `/app` folder in the container image back to your own machine's file system.  If you make a change, it will be immediately reflected in the version of the app running in Docker.**

### Running with Environment-specific Overrides

You have the option to use alternate override files, or alternate compose files entirely.  You could use this to run a production or model office configuration locally, using the exact same Docker image as the real environments.

The following example would start up ChatQuote from a previously built image (not from your file system's source code) and run it with a model office override file.  In general, we should not have environment specific override files in source control, because they contain environment variables with passwords in them.

But assuming you made your own `docker-compose.override.model.yml` file to test some issue, you would run the following command.

    docker-compose -f docker-compose.other.yml up

Each file to be used requires a `-f` property.  Files specified later on the command line override those earlier on the command line.  The filenames could be anything, such as `overrides-prod.yml` for something used for a prod environment.

By default, Docker will look to your `.env` file for the needed configuration.  If you wanted to use a different file, such as `.env.model`, you would specify it like this:

    docker-compose -f docker-compose.other.yml --env-file .env.model up

In order to get that to work, you would need many more environment variables to be defined.

If the `NODE_ENV` environment variable is set to `production` as it should be in any deployed environment, then the application will not allow for default values to be used and will, instead, complain and abort when it finds a missing env var at startup time.

Take a look at the included `SAMPLE.env.model` and `SAMPLE.env` files to see the difference.
