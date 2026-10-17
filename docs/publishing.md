# Publishing a parser

An official parser lives in its own repository, `OnFlyApp/ext-parser-<name>`, and is registered here by its release workflow. To get your parser listed as official, open an issue in [OnFlyApp/cli](https://github.com/OnFlyApp/cli/issues) first (language, extensions, repository link).

## Repository layout

Copy one of the existing parsers, for example [`ext-parser-python`](https://github.com/OnFlyApp/ext-parser-python):

- `main.go`: reads the file from stdin, takes the path from `argv[1]`, prints `[]Chunk` JSON.
- `Makefile`: `make wasm` builds `bin/<name>-parser.wasm` with `GOOS=wasip1 GOARCH=wasm CGO_ENABLED=0`, `-trimpath` and `-ldflags="-s -w -buildid="`. The build must be reproducible: the release job refuses to publish different bytes for an existing tag.
- `main_test.go`, `wasm_test.go`, `testdata/`: golden files for the chunks, and a test that runs the built wasm under wazero.
- `.github/workflows/test.yml` and `release.yml`, plus `dependabot.yml`.
- `THIRD_PARTY_NOTICES`: licenses of what is embedded in the wasm.

The chunk contract and the wasm calling convention are described in the [`cli` docs](https://github.com/OnFlyApp/cli/blob/main/docs/parsers.md).

## Release workflow

In `release.yml`, change the plugin name, the wasm file name, the build tags and the `--extensions` list. The job:

1. checks the tag is `vMAJOR.MINOR.PATCH` or `vMAJOR.MINOR.PATCH-rc.N` and that it is on `main`;
2. runs the tests and builds the wasm;
3. creates the GitHub release with `<name>-parser.wasm`, or verifies the existing release has identical bytes;
4. for a stable tag, runs `scripts/upsert.py` against a clone of this repo and pushes the commit.

`-rc.N` tags become GitHub pre-releases and are not registered. Install one by hand with `onfly ext install ./<name>-parser.wasm --extensions=".ext"`.

## Secret

Step 4 needs a `REGISTRY_TOKEN` secret in the parser repository: a token that can push to `OnFlyApp/registry`. Without it the job fails with `Authentication failed for OnFlyApp/registry.git`. Add the secret, then re-run the failed job. Nothing else is repeated, and the upsert is idempotent.

## Releasing

```sh
git tag v0.1.0
git push origin v0.1.0
```

The registry key you pass as `--plugin` decides the installed file name: `.onfly/plugins/<plugin>-parser.wasm`. When the job is green, check that `registry.json` has the new version and `onfly ext install <name>` works (allow a few minutes for the raw file cache).
