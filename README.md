# Soulseek Player (Android)

Native Android music-player prototype integrating Navidrome (Subsonic/OpenSubsonic) with recommendations from soulseek-queue.

## Source

The complete Android source archive is stored as eight base64 text parts under [source/encoded](source/encoded). Reassemble and extract it with:

```sh
mkdir -p app-src
cat source/encoded/part*.txt | base64 --decode | xz --decompress | tar -x -C app-src
```

See `app-src/README.md` for architecture, supported API methods, configuration and known limitations.

## CI

GitHub Actions reconstructs the source archive, runs JVM unit tests and builds a debug APK. A successful build publishes the APK as a downloadable workflow artifact (14-day retention).

## Status

This is an early implementation baseline, not a release-ready player. The CI result is the source of truth for whether the current revision compiles and its tests pass. No release APK is claimed until a successful build is produced.
