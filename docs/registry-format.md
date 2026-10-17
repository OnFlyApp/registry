# Registry format

`registry.json` is one JSON object. Each key is a plugin name, each value has `latest` and `versions`.

```json
{
  "rust": {
    "latest": "0.1.0",
    "versions": {
      "0.1.0": {
        "extensions": [".rs"],
        "sha256": "<64 hex>",
        "url": "https://github.com/OnFlyApp/ext-parser-rust/releases/download/v0.1.0/rust-parser.wasm"
      }
    }
  }
}
```

| Field | Rule |
|---|---|
| plugin name | `^[a-z0-9][a-z0-9._-]{0,63}$` |
| version | plain `MAJOR.MINOR.PATCH`, no `v` prefix, no pre-release suffix |
| `url` | `https://`, no spaces or `[]()` |
| `sha256` | 64 lowercase hex characters, the checksum of the file at `url` |
| `extensions` | lowercase, leading dot, at least one |
| `latest` | the highest version of the plugin, set by `scripts/upsert.py` |

## How Onfly uses it

Behavior of `onfly ext` as implemented in `internal/ext` of the `cli` repository.

- **Fetch.** The registry URL is `https://raw.githubusercontent.com/OnFlyApp/registry/main/registry.json`; `ONFLY_REGISTRY_URL` replaces it. The manifest is limited to 1 MiB, a plugin download to 64 MiB. Only `https` is accepted, including redirects.
- **`onfly ext install <plugin>[@version]`.** Resolves `latest` (or the pinned version). A release is rejected when its `url` is empty, its `sha256` is not 64 hex characters, or it has no `extensions`. The wasm is downloaded, its SHA-256 is compared with the registry value (mismatch: `ext: checksum mismatch`), and it is saved as `.onfly/plugins/<plugin>-parser.wasm`. The file name comes from the plugin key, not from the asset name in `url`. The release's `extensions` become a wasm parser entry in the project config, and `.onfly/plugins/installed.json` records version, file, checksum and extensions. If that version is already installed and the file and config entry match, it prints `<plugin> <version> is current`.
- **`onfly ext update [plugin]`.** Re-runs the install at `latest` for registry plugins, all of them or the named one. Local plugins are skipped (an explicit name for a local plugin is an error). An installed version newer than `latest` is left alone.
- **`onfly ext list`.** One row per installed plugin: `active`, `outdated` (the registry has a higher `latest`), or `corrupted` (the file on disk no longer matches the checksum recorded in `installed.json`). Local plugins show version `local`. The registry fetch times out after 3 seconds; on failure the table still prints, followed by a `registry:` line. With nothing installed it lists the plugin names the registry offers.

`raw.githubusercontent.com` can serve the previous file for a few minutes after a commit, so a new release may not be installable right away.

## Rules enforced by `scripts/upsert.py`

- A version, once registered, never changes: re-registering it with a different URL, checksum or extensions fails. Publish a new version instead.
- Re-running the script with identical values changes nothing, so a failed release job can be re-run safely.
- `latest` only moves up.
- The file is rewritten with sorted keys and two-space indentation.

Run `python3 scripts/upsert_test.py` to test the script.
