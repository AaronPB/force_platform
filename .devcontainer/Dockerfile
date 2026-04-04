FROM squidfunk/mkdocs-material:latest

RUN adduser -D -h /home/vscodeuser vscodeuser

WORKDIR /docs

RUN chown -R vscodeuser:vscodeuser /docs

USER vscodeuser
