# Framework-UI

## Install dependencies first

Make sure you run `yarn install` to download and install all of the needed dependencies for building and running the application.

### Running the application 🏃

UI is bootstrapped on create-react-app, so start it using `yarn start`
Backend node proxy server is started with `yarn server`.  Both need to be running.

The default `localhost` environment requires that MongoDB be running locally.  

#### Configuring Environment Variables

In order for the React application to compile and the server side component to be able to connect to a PML service, you will need to create a .env file in the project root that is modeled after the included `.env.example` file, shown below:

    NODE_PATH=src/
    SASS_PATH=src/
    CA_BUNDLE=/Users/{YOUR USERNAME}/certs/PML-CA_Bundle.pem
    KEY=/Users/{YOUR USERNAME}/certs/{YOUR NAME}.key
    CERT=/Users/{YOUR USERNAME}/certs/{YOUR NAME}.pem

Note that the example paths in `.env.example` assume you are running a Mac or Linux based machine.  Change to back slash characters for Windows.

You could skip this step if you have another preferred way of specifying environment variables, such as in your IDE.

#### WebStorm Setup

While setting `NODE_PATH` as noted above will ensure that the compiler knows where to find your components, WebStorm will not work fully unless you take additional action.

In the WebStorm file explorer, you will want to right click on the `src` folder and go to near the bottom of the pop-up menu and select "Mark Directory As" and choose the "Resource Root" option.  This will allow WebStorm to find the code you `import` from you other modules without having to specify a full relative path to it.

In other words, WebStorm will understand that `import blah from 'components/blah'` is to be found in `src/components/blah` or `server/components/blah`, preventing it from falsely complaining about unused imports and such.  Otherwise you would have to do something like `import blah from '../../components/blah'`.

#### Client Security Certificates

The example `.env` file also assumes that you have a personal cert, private key, and CA Bundle file in a folder called `certs` off of your home folder (e.g. `~/certs`).  In most cases, the key and cert file are named after you.  If that is not the case, update the paths as needed.

    CA_BUNDLE=/Users/jdoe/certs/PML-CA_Bundle.pem
    KEY=/Users/jdoe/certs/John Doe.key
    CERT=/Users/jdoe/certs/John Doe.pem

### Architecture 🏗

UI code is kept in `src`, and the node server code is kept in `server`. Components are broken into 3 main sections, `components`, `views`, and `componentLibrary`. Typically, the flow is that simple UI components are kept in `components`, which build upon the `componentLibrary` components if feasible, and are used to build larger application views (pages), which are kept in `views`.

This codebase is using the most current version of React (`16.8` at the time of writing), and developers are encouraged to use modern React conventions such as hooks and the context API. Functional components are encouraged, but Class components can still be used to access lifecycle methods. Currently, we are avoiding using Redux, as most things can be achieved using hooks and context. 

Tests are being written using Jest, and those will be scoped on the component level, placed next to the relevant component. Tests can be ran by running `yarn test`

In order to return data while developing the application, developers will need to pass an SSO token into the request header. Until OAuth/SSO is established, you can do this by modifying the token at `server/config/environment/index.js`. You can generate a new token using this [URL](http://devcommonws01.pennmutual.com:8080/ui-util/#token). If you don't have access to this, contact Ryan Adams. 

### Branching strategy 🌳

This project uses the [git flow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow) workflow. 

Feature branches should be created for new functionality (e.g. `features/new_cool_thing`).

