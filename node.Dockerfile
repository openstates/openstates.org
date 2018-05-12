FROM node:8.9-slim

RUN mkdir -p /opt/openstates.org/
ADD . /opt/openstates.org
WORKDIR /opt/openstates.org

# RUN /bin/bash -l -c "nvm install"
# RUN /bin/bash -l -c "nvm use"
RUN npm install
RUN npm run build
