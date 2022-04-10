FROM eidos-service.di.unito.it/eidos-base-pytorch:1.10.0

# Copy source files and make it owned by the group eidoslab
# and give write permission to the group
COPY src /src
RUN chmod 775 /src
RUN chown -R :1337 /src

# Do the same with the data folder (default /data)
# you can change the path as you wish
RUN mkdir /data
RUN chmod 775 /data
RUN chown -R :1337 /data

WORKDIR /src

ENTRYPOINT ["python3"]