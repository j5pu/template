# syntax=docker/dockerfile:1

FROM python:3.11-slim-buster

ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install --upgrade -q pip && pip install -q --no-cache-dir envg[dev]