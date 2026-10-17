# Onfly plugin registry

Onfly reads `https://raw.githubusercontent.com/OnFlyApp/registry/main/registry.json`.

`raw.githubusercontent.com` can serve a previous file for a few minutes after a commit.

## Plugins

Install with `onfly ext install <plugin>`.

| Plugin | Extensions | Repository | Latest |
|---|---|---|---|
| `go` | `.go` | [`ext-parser-go`](https://github.com/OnFlyApp/ext-parser-go) | 0.1.0 |
| `javascript` | `.js`, `.jsx`, `.mjs`, `.cjs` | [`ext-parser-javascript`](https://github.com/OnFlyApp/ext-parser-javascript) | 0.1.0 |
| `php` | `.php`, `.phtml`, `.inc` | [`ext-parser-php`](https://github.com/OnFlyApp/ext-parser-php) | 0.1.0 |
| `python` | `.py`, `.pyi` | [`ext-parser-python`](https://github.com/OnFlyApp/ext-parser-python) | 0.1.0 |
| `rust` | `.rs` | [`ext-parser-rust`](https://github.com/OnFlyApp/ext-parser-rust) | 0.1.0 |
| `typescript` | `.ts`, `.tsx`, `.mts`, `.cts` | [`ext-parser-typescript`](https://github.com/OnFlyApp/ext-parser-typescript) | 0.1.0 |

## Docs

- [Registry format](docs/registry-format.md): fields, validation rules and how Onfly reads the file.
- [Publishing a parser](docs/publishing.md): repository layout, release workflow, secret and tagging.

## Format

`registry.json` maps a plugin key to an object with `latest` and `versions`. Each version has:

- `url`: plain `https` link to the `.wasm` asset
- `sha256`: 64 hex characters
- `extensions`: file extensions the parser handles, lowercase with a leading dot

```json
{
  "go": {
    "latest": "0.1.0",
    "versions": {
      "0.1.0": {
        "extensions": [".go"],
        "sha256": "0a7d…8afb",
        "url": "https://github.com/OnFlyApp/ext-parser-go/releases/download/v0.1.0/go-parser.wasm"
      }
    }
  }
}
```

## Adding a parser

Do not open a pull request against this repo. A parser lives in its own repository, `OnFlyApp/ext-parser-<name>`, with the same `test.yml` and `release.yml` workflows as the existing ones and a `REGISTRY_TOKEN` secret that can push to this repo. Pushing a `vMAJOR.MINOR.PATCH` tag builds the wasm, publishes the GitHub release and updates this registry. `-rc.N` tags are pre-releases and are not registered. See the [`cli` repository](https://github.com/OnFlyApp/cli) for the parser contract.

To have your own parser listed here as an official one, open an issue in [OnFlyApp/cli](https://github.com/OnFlyApp/cli/issues) with the request: the language, the extensions it handles, and a link to its repository.

## Releases

Plugin CI calls `scripts/upsert.py`:

```sh
python3 scripts/upsert.py registry.json \
  --plugin go --version 0.1.0 \
  --url https://github.com/OnFlyApp/ext-parser-go/releases/download/v0.1.0/go-parser.wasm \
  --sha256 <64 hex> --extensions .go
```

- Plugin names match `^[a-z0-9][a-z0-9._-]{0,63}$`; versions are plain `MAJOR.MINOR.PATCH`.
- Changing the checksum of an existing version fails.

Run the tests with `python3 scripts/upsert_test.py`.

## Author

[Oleksii Ivanov](https://github.com/axitdev)

## License

Licensed under the **Functional Source License, Version 1.1, ALv2 Future License** (SPDX: `FSL-1.1-ALv2`), see [LICENSE](LICENSE).

Free for any purpose other than a competing use: making the software available in a commercial product or service that substitutes for it. Each version converts to Apache 2.0 two years after it is released.
