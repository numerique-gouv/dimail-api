FROM debian:latest

RUN apt-get update
RUN apt install -y wget
RUN wget -qO- https://packages.adoptium.net/artifactory/api/gpg/key/public | tee /etc/apt/trusted.gpg.d/adoptium.asc
RUN echo 'deb https://packages.adoptium.net/artifactory/deb bookworm main' > /etc/apt/sources.list.d/adoptium.list
RUN wget -qO- https://software.open-xchange.com/0xDFD4BCF6-oxbuildkey.pub | tee /etc/apt/trusted.gpg.d/ox.asc
RUN echo 'deb https://software.open-xchange.com/products/appsuite/stable/backend/DebianBullseye /' > /etc/apt/sources.list.d/ox.list
RUN echo 'deb https://software.open-xchange.com/products/appsuite/stable/appsuiteui/DebianBullseye /' >> /etc/apt/sources.list.d/ox.list

RUN apt-get update
RUN apt-get install -y temurin-8-jdk open-xchange open-xchange-admin open-xchange-authentication-imap


RUN apt-get install -y openssh-server openssh-client

WORKDIR /etc/ssh
COPY --chmod=400 ./ssh_host_ecdsa_key ./ssh_host_ecdsa_key.pub ./
COPY --chmod=400 ./ssh_host_ed25519_key ./ssh_host_ed25519_key.pub ./
COPY --chmod=400 ./ssh_host_rsa_key ./ssh_host_rsa_key.pub ./

WORKDIR /root
COPY ./authorized_keys ./.ssh/authorized_keys
COPY --chmod=0755 ./setup.sh ./purge.sh ./

RUN mkdir /run/sshd

ENTRYPOINT ["/root/setup.sh"]

EXPOSE 22
