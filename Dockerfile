# Hardened serving image (Lab 7.1): pinned base digests, multi-stage, distroless, non-root.
# Resolve the digests for your platform (Lab 7.1 Part 2) and pass them with --build-arg:
#   docker manifest inspect python:3.12-slim --verbose | jq -r '.[0].Descriptor.digest // .Descriptor.digest'
#   docker manifest inspect gcr.io/distroless/python3-debian12:nonroot --verbose | jq -r '.[0].Descriptor.digest // .Descriptor.digest'
ARG SLIM_DIGEST=sha256:REPLACE_ME
ARG DISTROLESS_DIGEST=sha256:REPLACE_ME

FROM python:3.12-slim@${SLIM_DIGEST} AS build
WORKDIR /w
COPY requirements-serve.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements-serve.txt
ARG COSIGN_VERSION=2.4.1
ADD https://github.com/sigstore/cosign/releases/download/v${COSIGN_VERSION}/cosign-linux-amd64 /usr/local/bin/cosign
RUN chmod 755 /usr/local/bin/cosign

FROM gcr.io/distroless/python3-debian12:nonroot@${DISTROLESS_DIGEST}
ENV PYTHONPATH=/install/lib/python3.12/site-packages:/app
COPY --from=build /install /install
COPY --from=build /usr/local/bin/cosign /usr/local/bin/cosign
COPY src/ /app/src/
COPY model/ /app/model/
COPY cosign.pub /app/cosign.pub
WORKDIR /app
USER 65532:65532
EXPOSE 8080
ENTRYPOINT ["python", "-m", "uvicorn", "src.serve:app", "--host", "0.0.0.0", "--port", "8080"]
