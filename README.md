docker-based build environments for static (linux x86_64) binaries

```
./build base-*
./build ...
```

todo:

- better final binary naming (add gcc and glibc version)
- automated basic build + test in CI before i upgrade the bases
    - probably want to upload bases to docker hub and pin versions
- work towards more reproducible builds
    - building static libjpeg ourselves, for example
    - or, find a way to pin debian package versions
