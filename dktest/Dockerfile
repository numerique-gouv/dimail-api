FROM debian:latest

RUN apt-get update
RUN apt-get install -y opendkim openssl
RUN apt-get install -y openssh-server openssh-client

WORKDIR /etc/ssh
COPY --chmod=400 ./ssh_host_ecdsa_key ./ssh_host_ecdsa_key.pub ./
COPY --chmod=400 ./ssh_host_ed25519_key ./ssh_host_ed25519_key.pub ./
COPY --chmod=400 ./ssh_host_rsa_key ./ssh_host_rsa_key.pub ./

WORKDIR /root
COPY authorized_keys* ./.ssh/
COPY --chmod=0755 ./setup.sh ./make_dkim.sh ./


RUN mkdir /run/sshd

ENTRYPOINT ["/root/setup.sh"]

EXPOSE 22
