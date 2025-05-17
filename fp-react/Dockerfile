#You should pass in Environment variables from a Docker Compose file, not from here
#FROM node:14.18.1 as base
FROM 939625251876.dkr.ecr.us-east-1.amazonaws.com/base/nodejs-pml-16:latest-dev as base
ENV DOCKER_RUNNING=true
EXPOSE 3000
WORKDIR /app
RUN yarn global add nodemon
COPY --chown=nodejs:nodejs public /app/public
COPY --chown=nodejs:nodejs package.json /app

# Common to dev and deployed servers
FROM base as baseserver
COPY --chown=nodejs:nodejs server /app/server

# Do server productionized yarn install (w/o dev dependencies)
FROM baseserver as serverbuild
WORKDIR /app/server
RUN yarn --frozen-lockfile --production install

# Install dependencies (including dev) to support reactbuild or devreactserver
FROM base as react
COPY --chown=nodejs:nodejs src /app/src
COPY --chown=nodejs:nodejs craco.config.js /app
COPY --chown=nodejs:nodejs jsconfig.json /app
COPY --chown=nodejs:nodejs yarn.lock /app
# network-concurrency can be set due to issue: https://github.com/yarnpkg/yarn/issues/2629#issuecomment-283691556
# set it to 1 if you see errors like: "Extracting tar content of undefined failed, the file appears to be corrupt"
# This is mostly tied to Git dependencies pulled from BitBucket rather than the NPM registry
RUN yarn install

# Use Webpack to compile the React web application into /app/build
FROM react AS reactbuild
RUN yarn build

# Build the deployable server image using a lean node base, making use of the Webpack-compiled files
#FROM node:14.18.1-slim as server
FROM 939625251876.dkr.ecr.us-east-1.amazonaws.com/base/nodejs-pml-16:latest-slim as server
ARG build_tag=UNSET
ENV BUILD_TAG=$build_tag
ENV DOCKER_RUNNING=true
WORKDIR /app/server
COPY --chown=nodejs:nodejs --from=reactbuild /app/build /app/build
COPY --chown=nodejs:nodejs --from=serverbuild /app/server /app/server
COPY --chown=nodejs:nodejs --from=serverbuild /app/package.json /app/package.json
CMD ["node", "server.js"]

# Local development stage - node server
FROM baseserver as devnodeserver
ARG appVersion=UNSET
ENV APP_VERSION=$appVersion
WORKDIR /app/server
RUN yarn install
CMD [ "nodemon", "server.js" ]

# Local development stage - webpack dev server
FROM react as devreactserver
CMD [ "yarn", "start" ]
