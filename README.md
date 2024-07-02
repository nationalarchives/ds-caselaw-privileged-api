# The National Archives: Find Case Law

This repository is part of the [Find Case Law](https://caselaw.nationalarchives.gov.uk/) project at [The National Archives](https://www.nationalarchives.gov.uk/). For more information on the project, check [the documentation](https://github.com/nationalarchives/ds-find-caselaw-docs).

# API Server

Exposing an API to archived case law.

## Requirements.

Python >= 3.12

## Installation & Usage

Ensure that the `MARKLOGIC_API_CLIENT_HOST` environment is set to point at the Marklogic server.

This project uses [Poetry](https://python-poetry.org/) to manage dependencies. You can install them with `poetry install`, and access a virtual environment with `poetry shell`.

To run the server, run `script/server`; open `http://localhost:8080/` in a browser

## Documentation

Run the server and check `http://localhost:8080/docs/`

## Running with Docker (untested)

To run the server on a Docker container, please execute the following from the root directory:

```bash
docker-compose up --build
```

## Tests

Run `script/test`

## Linting

Run `pre-commit install` to set up linting, and/or copy the `pre-push.sample` file to `.github/hooks/pre-push`

## Deployment

### Staging

The `main` branch is automatically deployed with each commit. The deployed API Swagger docs can be viewed at
[https://api.staging.caselaw.nationalarchives.gov.uk/docs](https://api.staging.caselaw.nationalarchives.gov.uk/docs)

### Production

To deploy to production:

1. Create a [new release](https://github.com/nationalarchives/ds-caselaw-privileged-api/releases).
2. Set the tag and release name to `vX.Y.Z`, following semantic versioning.
3. Publish the release.
4. Automated workflow will then force-push that release to the `production` branch, which will then be deployed to the
   production environment.

The production Swagger API docs are at
[https://api.caselaw.nationalarchives.gov.uk/docs](https://api.caselaw.nationalarchives.gov.uk/docs)
