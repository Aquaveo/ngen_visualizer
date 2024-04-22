################################################################################################################
##### External Global Args Declaration and Defaults
################################################################################################################
ARG REPO_URL=https://github.com/Aquaveo/ngen_visualizer.git \
    BRANCH=main

FROM tethysplatform/tethys-core:dev

###################
# BUILD ARGUMENTS #
###################

ARG MICRO_TETHYS=true \
    REPO_URL \
    BRANCH \
    MAMBA_DOCKERFILE_ACTIVATE=1

###############
# ENVIRONMENT #
###############
ENV TETHYS_DB_ENGINE=django.db.backends.sqlite3
ENV TETHYS_DB_NAME=
ENV TETHYS_DB_USERNAME=
ENV TETHYS_DB_PASSWORD=
ENV TETHYS_DB_HOST=
ENV TETHYS_DB_PORT=
ENV ENABLE_OPEN_PORTAL=True
ENV PORTAL_SUPERUSER_NAME=admin
ENV PORTAL_SUPERUSER_PASSWORD=pass
#############
# ADD FILES #
#############
RUN git clone --single-branch --branch $BRANCH $REPO_URL \ 
    && cd ngen_visualizer \ 
    && micromamba install --yes -c conda-forge --file requirements.txt \ 
    && micromamba clean --all --yes \
    && tethys install -d -N 


#########
# PORTS #
#########
EXPOSE 80

#######
# RUN #
#######
WORKDIR ${TETHYS_HOME}
CMD bash run.sh