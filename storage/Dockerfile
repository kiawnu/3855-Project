FROM python:3

LABEL maintainer="kabdollahi@my.bcit.ca"

RUN mkdir /app
RUN mkdir -p /app/data
RUN mkdir -p /app/logs
RUN mkdir -p /app/config
# We copy just the requirements.txt first to leverage Docker cache
# on `pip install`

COPY ./requirements.txt /app/requirements.txt

# Set the working directory
WORKDIR /app

# Install dependencies
RUN pip3 install -r requirements.txt

# Copy the source code
COPY . /app


COPY ./wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Change permissions and become a non-privileged user
RUN chown -R nobody:nogroup /app
USER nobody



# Tells on which port the service listens in the container
EXPOSE 8090

# Entrypoint = run Python
ENTRYPOINT [ "/bin/bash" ]

# Default = run app.py
CMD [ "-c", "/usr/local/bin/wait-for-it.sh db:3306 -- python3 db.py && python3 app.py" ]