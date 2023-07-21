# docker build -t find3 .
# mkdir /tmp/find3
# docker run -p 11883:1883 -p 8003:8003 -v /tmp/find3:/data -t find3

FROM ubuntu:18.04


ENV GOLANG_VERSION 1.17
ENV PATH="/usr/local/go/bin:/usr/local/work/bin:${PATH}"
ENV GOPATH /usr/local/work
ENV GO111MODULE=on

# RUN python3 -m pip install --upgrade pip

# RUN apt-get update && apt-get -y upgrade && \
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \ 
	wget git libc6-dev make pkg-config g++ gcc mosquitto-clients mosquitto python3 python3-dev \ 
	python3-pip python3-matplotlib \
	python3-setuptools python3-wheel supervisor libfreetype6-dev libopenblas-dev libblas-dev \
	liblapack-dev gfortran
RUN	python3 -m pip install Cython --install-option="--no-cython-compile"
# RUN python3 -m pip install Cython \
RUN	apt-get install --no-install-recommends -y python3-scipy python3-numpy python3-pandas

# RUN apt update && apt install -y tcl
# RUN python3 -m pip install --upgrade pip
# RUN pip install numpy scipy matplotlib pandas
RUN	mkdir /usr/local/work
RUN	rm -rf /var/lib/apt/lists/* 
RUN	set -eux; 
# this "case" statement is generated via "update.sh"
RUN DPKGARCH="$(dpkg --print-architecture)"; \
    case "${dpkgArch##*-}" in \
      amd64) goRelArch='linux-amd64'; goRelSha256='8a3a2296b65803a58e90952cc4c72f5d89023f279db3ade5ea9a4fb1284a6e3d' ;; \
      armhf) goRelArch='linux-armv6l'; goRelSha256='a3a5d4bc401b6f503cd4027d24e0ea9c9770a5d0c4409b6bc5d7be600f1eec6e' ;; \
      arm64) goRelArch='linux-arm64'; goRelSha256='72fc5b144f8ab9ea49ab4551a1400d1441fb89c6b0441f6b1a8a6a1e488eb569' ;; \
      i386) goRelArch='linux-386'; goRelSha256='e5a32937a0d4898b6fa40156f1d79f1e73429660df90f8f61b0c50b3b6191a83' ;; \
      ppc64el) goRelArch='linux-ppc64le'; goRelSha256='5e8065223c9b44905edbbf736b87b923b7c80e75100cab9ad5ba3d6cd6a84ed8' ;; \
      s390x) goRelArch='linux-s390x'; goRelSha256='f9d5426ae4b5b1064b14e5f3d6a5a5560697586b76c1a2f7943f7f1cd1c01468' ;; \
      *) goRelArch='src'; goRelSha256='af360a66a2089732fa75b373c105d662186a9c2dd83afe1f2db8738e64c1420c'; \
         echo >&2; echo >&2 "warning: current architecture ($dpkgArch) does not have a corresponding Go binary release; will be building from source"; echo >&2 ;; \
    esac; \
    url="https://golang.org/dl/go${GOLANG_VERSION}.${goRelArch}.tar.gz"; \
    wget -O go.tgz "$url"; \
    echo "${goRelSha256} *go.tgz" | sha256sum -c -; \
    tar -C /usr/local -xzf go.tgz; \
    rm go.tgz; \
    if [ "$goRelArch" = 'src' ]; then \
      echo >&2; \
      echo >&2 'error: UNIMPLEMENTED'; \
      echo >&2 'TODO install golang-any from jessie-backports for GOROOT_BOOTSTRAP (and uninstall after build)'; \
      echo >&2; \
      exit 1; \
    fi; \
    export PATH="/usr/local/go/bin:$PATH"; \
    go version && \
	mkdir /build && cd /build && \
	git clone https://github.com/Nimaapr/find3.git && \
	mkdir /data && \
	mkdir /app && \
	echo '#!/bin/bash\n\
pkill -9 mosquitto\n\
cp -R -u -p /app/mosquitto_config /data\n\
mosquitto -d -c /data/mosquitto_config/mosquitto.conf\n\
mkdir -p /data/logs\n\
/usr/bin/supervisord\n'\
> /app/startup.sh && \
	chmod +x /app/startup.sh && echo '[supervisord]\n\
nodaemon=true\n\
[program:main]\n\
directory=/app/main\n\
command=/app/main/main -debug -data /data/data -mqtt-dir /data/mosquitto_config\n\
priority=1\n\
stdout_logfile=/data/logs/main.stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/data/logs/main.stderr\n\
stderr_logfile_maxbytes=0\n\
[program:ai]\n\
directory=/app/ai\n\
command=make production\n\
priority=2\n\
stdout_logfile=/data/logs/ai.stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/data/logs/ai.stderr\n\
stderr_logfile_maxbytes=0\n'\
> /etc/supervisor/conf.d/supervisord.conf && \
	mkdir /app/mosquitto_config && \
	touch /app/mosquitto_config/acl  && \
	touch /app/mosquitto_config/passwd  && echo 'allow_anonymous false\n\
acl_file /data/mosquitto_config/acl\n\
password_file /data/mosquitto_config/passwd\n\
pid_file /data/mosquitto_config/pid\n'\
> /app/mosquitto_config/mosquitto.conf && \
	echo "moving to find3" && cd /build/find3/server/main  && go build -v && \
	echo "moving main" && mv /build/find3/server/main /app/main && \
	echo "moving to ai" && cd /build/find3/server/ai  && python3 -m pip install -r requirements.txt && \
	echo "moving ai" && mv /build/find3/server/ai /app/ai && \
	echo "removing go srces" && rm -rf /usr/local/work/src && \
	echo "purging packages" && apt-get remove -y --auto-remove git libc6-dev pkg-config g++ gcc && \
	echo "autoclean" && apt-get autoclean && \
	echo "clean" && apt-get clean && \
	echo "autoremove" && apt-get autoremove && \
	echo "rm trash" && rm -rf ~/.local/share/Trash/* && \
	echo "rm go" && rm -rf /usr/local/go* && \
	echo "rm perl" && rm -rf /usr/share/perl* && \
	echo "rm build" && rm -rf /build* && \
	echo "rm doc" && rm -rf /usr/share/doc* 

WORKDIR /app
CMD ["/app/startup.sh"]
