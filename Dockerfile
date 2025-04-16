FROM python:3.10.3-slim 

RUN apt-get update -o Acquire::Retries=3  && apt-get install -y --no-install-recommends \
                vim \
                automake \
                build-essential \
                yasm \
		        cmake \
                git \
                libboost-dev \
                libboost-thread-dev \
                libclang-dev \
                libgmp-dev \
                libntl-dev \
                libsodium-dev \
                libssl-dev \
                libtool \
                valgrind \
                texinfo \
                clang \
                curl \
                zlib1g-dev \
                && rm -rf /var/lib/apt/lists/*



COPY . /MPCGuard

WORKDIR /MPCGuard

RUN pip install -r requirements.txt

WORKDIR /MPCGuard/frameworks/MP-SPDZ

RUN rm -rf deps
RUN git init
RUN make clean-deps boost libote 
RUN make -j8 tldr && make -j8 semi2k-party.x replicated-ring-party.x 

WORKDIR /MPCGuard/frameworks/tf-encrypted

RUN make build

WORKDIR /MPCGuard

CMD ["/bin/bash"]
