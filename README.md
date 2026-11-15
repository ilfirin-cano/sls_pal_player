# Soulseek Player (Android)

Native Android music-player prototype integrating Navidrome (Subsonic/OpenSubsonic) with recommendations from soulseek-queue.

## Source

The complete Android project is archived at [source/soulseek-player-source.tar.xz](source/soulseek-player-source.tar.xz). Extract it with:

```sh
mkdir app-src
tar -xJf source/soulseek-player-source.tar.xz -C app-src
```

See `app-src/README.md` for architecture, supported API methods, configuration and known limitations.

## CI

GitHub Actions extracts the source, runs JVM unit tests and builds a debug APK. The APK is published as a workflow artifact when the workflow succeeds.

## Status

This is an early implementation baseline, not a release-ready player. The CI result is the source of truth for whether the current revision compiles and its tests pass. No release APK is claimed until a successful build is produced.
