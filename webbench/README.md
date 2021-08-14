# webbench

go implement [webbench](http://home.tiscali.cz/~cz210552/webbench.html)

## usage

```bash
./webbench -h
  -c, --client int      Run <n> HTTP clients at once. (default 1)
  -f, --force           Don't wait for reply from server.
  -m, --method string   Use request methods with get/head/options/trace. (default "get")
  -r, --reload          Send reload request - Pragma: no-cache.
  -t, --time int        Run benchmark for <sec> seconds. (default 30)
```

