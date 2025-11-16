# Redirection Junction - ANALYSIS UPDATE

## Challenge Information
- **Platform**: UWSP Pointer Overflow CTF
- **Category**: Web
- **Difficulty**: Easy
- **Target**: https://web100-4.pointeroverflowctf.com

## Summary
**New Discovery (2025-11-11):** Detailed analysis reveals a self-referential token chain that creates a redirection loop. Previous attempts missed the loop detection mechanism. The `/final` endpoint returns "Incomplete final request" until specific conditions are met. Current working hypothesis: need to track sequence of tokens visited before accessing `/final`.

## Updated Findings

### Self-Referential Token Chain Discovery
New analysis shows the chain enters a self-referential loop:
- Initial chain: `/` → `/start` → `/step_js` (sets cookie) → `/step_meta/bWV0YS10b2tlbi0x` → `/meta_decode/bWV0YS10b2tlbi0x` → `/step_meta/meta-token-1`
- At `/step_meta/meta-token-1`, the payload is `meta-token-1` (plaintext, not encoded)
- This suggests the chain should proceed: `/meta_decode/meta-token-1` → (next token)
- However: `/meta_decode/meta-token-1` returns 400 "Invalid payload"

**Critical insight:** The payload at `/step_meta/meta-token-1` is plaintext "meta-token-1", not base64 encoded. To continue, it must be re-encoded: `base64("meta-token-1")` = `bWV0YS10b2tlbi0x`.

### Why Previous Attempts Failed
1. **Loop detection missed:** Did not recognize `/step_meta/meta-token-1` shows plaintext payload
2. **Re-encoding required:** At meta-token-1 level, payload must be base64 re-encoded before visiting `/meta_decode/`
3. **Incomplete /final request:** Still returns "Incomplete final request" even after following chain correctly

### Redirection Chain Analyzed

#### Step 1: Root (/)
- **Status**: 302
- **Redirects to**: `/start`
- **Cookies**: None

#### Step 2: /start
- **Status**: 302
- **Redirects to**: `/step_js`
- **Cookies**: None
- **Referer sent**: `https://web100-4.pointeroverflowctf.com`

#### Step 3: /step_js
- **Status**: 200
- **Cookies SET**: `visited_js=1` (must preserve for all subsequent requests)
- **Referer sent**: `https://web100-4.pointeroverflowctf.com/start`
- **Contains**: JavaScript with Base64-encoded path
  - Payload: `L3N0ZXBfbWV0YS9iV1YwWVMxMGIydGxiaTB4`
  - First decode: `/step_meta/bWV0YS10b2tlbi0x`
  - **JavaScript comment says "decode twice" - this is the key hint**
- **Next URL**: `/step_meta/bWV0YS10b2tlbi0x`

#### Step 4: /step_meta/bWV0YS10b2tlbi0x
- **Status**: 200
- **Cookies**: `visited_js=1` (carried forward)
- **Referer sent**: `https://web100-4.pointeroverflowctf.com/step_js`
- **Contains**: Meta refresh tag and encoded payload
  - Meta refresh: `content="0;url=/meta_decode/bWV0YS10b2tlbi0x"`
  - Encoded payload shown: `bWV0YS10b2tlbi0x`
  - **Payload decodes to**: `meta-token-1`
- **Next URL**: `/meta_decode/bWV0YS10b2tlbi0x`

#### Step 5: /meta_decode/bWV0YS10b2tlbi0x
- **Status**: 302
- **Cookies**: `visited_js=1` (carried forward)
- **Referer sent**: `https://web100-4.pointeroverflowctf.com/step_meta/bWV0YS10b2tlbi0x`
- **Location header**: `meta-token-1`
- **Next URL**: `/step_meta/meta-token-1`

#### Step 6: /step_meta/meta-token-1
- **Status**: 200
- **Cookies**: `visited_js=1` (carried forward)
- **Referer sent**: `https://web100-4.pointeroverflowctf.com/meta_decode/bWV0YS10b2tlbi0x`
- **Contains**: Meta refresh tag
  - Meta refresh: `content="0;url=/meta_decode/meta-token-1"`
  - **Payload shown is plaintext**: `meta-token-1` (not base64 encoded)
- **Key finding**: Payload is NOT base64 - must re-encode to continue chain

#### Step 7: /meta_decode/meta-token-1 (with correct encoding)
- **Expected**: 302 redirect to next token in sequence
- **Actual**: 400 "Invalid payload"
- **Analysis**: May require integer increment of token number (meta-token-2, meta-token-3, etc.)

## What Makes This Challenge Work

### The Double-Decode Hint
JavaScript comment: "payload is a base64 of the target path. To make it slightly obfuscated we decode twice."

This means:
1. Decode JavaScript: `L3N0ZXBfbWV0YS9iV1YwWVMxMGIydGxiaTB4` → `/step_meta/bWV0YS10b2tlbi0x`
2. Take path component: `bWV0YS10b2tlbi0x` → `meta-token-1` (first decode)
3. But can we operate on `meta-token-1` further? Maybe increment the number?

### Token Pattern
Pattern appears to be sequential: meta-token-1, meta-token-2, meta-token-3, ...
Based on testing meta-token-1 through meta-token-50, structure is consistent.

### /final Endpoint Behavior
Returns "Incomplete final request" until specific conditions met. Possible conditions:
- X number of tokens visited
- Specific token reached (meta-token-N where N is special number)
- Accumulating tokens in cookie or header
- POST request with accumulated token data

## Attempts Made (New)

### 1. Self-Referential Loop Detection
- Identified that `/step_meta/meta-token-1` payload is plaintext
- Discovered need to re-encode before `/meta_decode/`
- Still results in 400 or loop

### 2. Sequential Token Testing
- Tested tokens 1-50 following pattern
- All tokens behave consistently
- No "final" token found in range 1-50

### 3. Re-Encoding Logic
```python
# At meta-token level, payload is plaintext
plaintext_payload = "meta-token-1"
encoded_payload = base64.b64encode(plaintext_payload.encode()).decode()
# Result: "bWV0YS10b2tlbi0x"
# Then visit: /meta_decode/bWV0YS10b2tlbi0x
```

### 4. /final Endpoint Variations
- Tried after each token
- Tried with query parameters (token=, payload=, meta-token-1=)
- Tried with custom headers (X-Token, X-Payload)
- Tried POST with form data
- Tried after all tokens 1-50
- **Result**: Always "Incomplete final request"

## Updated Assumptions Made

1. **JavaScript double-decode is operational hint:** May indicate two-phase decoding or sequential operations
2. **Token sequence matters:** May need to visit tokens in incrementing order
3. **State accumulation:** Some state (cookies, headers, session data) must accumulate across requests
4. **/final requires accumulated data:** The "incomplete" message suggests missing accumulated token data
5. **Loop is intentional:** The self-referential loop may be the challenge mechanism

## Questions/Uncertainties (Updated)

1. **What's the trigger for /final to work?** "Incomplete final request" suggests missing completion condition
2. **Is there a secret token number?** Maybe meta-token-100, meta-token-0, or meta-token-final?
3. **Does order matter beyond sequence?** Maybe need to visit some tokens before others
4. **Is there a timing component?** Maybe need to visit tokens within time window
5. **Are we missing a cookie?** Only `visited_js=1` is ever set - maybe others set under conditions
6. **What does "decode twice" really mean operationally?**
7. **Is the payload accumulation pattern wrong?** Maybe need to concatenate or hash tokens

## Files Created (New Analysis)

- `manual_test.py` - Manual step-by-step verification
- `test_browser_behavior.py` - Browser-like request simulation
- `detailed_inspection.py` - Detailed response inspection
- `cookie_tracking_test.py` - Cookie and state tracking
- `test_double_decode.py` - JavaScript double-decode analysis
- `test_both_paths.py` - Both single/double decode paths tested
- `follow_new_chain.py` - Follow discovered chain pattern
- `follow_token_sequence.py` - Sequential token testing (1-50)
- `check_meta_decode_cookies.py` - Cookie analysis at each step
- `follow_complete_chain.py` - Complete chain with loop detection
- `solution_attempt.py` - Comprehensive solution with analysis

## Next Steps for Someone Else

1. **Determine /final completion condition:** The "Incomplete final request" is the key clue. Figure out what makes it complete.

2. **Investigate token accumulation mechanism:** How should tokens be accumulated or combined? Try:
   - Concatenating all tokens into one string
   - Hashing tokens (MD5, SHA1, etc.)
   - Using tokens as keys in a dictionary structure
   - Submitting all visited tokens to /final

3. **Look for hidden state:** Check:
   - LocalStorage or SessionStorage values (requires JavaScript execution)
   - Additional cookies set by intermediate steps
   - Hidden form fields or comments in HTML
   - Special headers in responses

4. **Analyze "decode twice" operationally:** The JavaScript hint might mean:
   - Two tokens must be decoded and combined
   - Decode, operate, then decode again (increment token number?)
   - First decode gets path, second decode reveals token manipulation method

5. **Timing or sequence attack:** Try:
   - Rapid sequential requests
   - Specific delays between requests
   - Requesting tokens in specific non-sequential order

6. **Check challenge server for hints:** Server is Werkzeug/3.1.3 - check for debug mode or error pages that reveal information

7. **Review challenge on CTF platform:** May have hints, updates, or comments from other players

## Redirect Chain Followed

### Step 1: Root (/)
- **Status**: 302
- **Redirects to**: `/start`
- **Cookies**: None

### Step 2: /start
- **Status**: 302
- **Redirects to**: `/step_js`
- **Cookies**: None
- **Referer sent**: `https://web100-4.pointeroverflowctf.com`

### Step 3: /step_js
- **Status**: 200
- **Cookies SET**: `visited_js=1` (preserved in all subsequent requests)
- **Referer sent**: `https://web100-4.pointeroverflowctf.com/start`
- **Contains**: JavaScript with double-encoded Base64 payload
  - Payload: `L3N0ZXBfbWV0YS9iV1YwWVMxMGIydGxiaTB4`
  - First decode: `/step_meta/bWV0YS10b2tlbi0x`
  - JavaScript attempts second decode but fails (contains `/`), uses first decode
- **Next URL**: `/step_meta/bWV0YS10b2tlbi0x`

### Step 4: /step_meta/bWV0YS10b2tlbi0x
- **Status**: 200
- **Cookies**: `visited_js=1` (carried forward)
- **Referer sent**: `https://web100-4.pointeroverflowctf.com/step_js`
- **Contains**: Meta refresh tag
  - Points to: `/meta_decode/bWV0YS10b2tlbi0x`
  - Also displays encoded payload: `bWV0YS10b2tlbi0x` which decodes to `meta-token-1`
- **Next URL**: `/meta_decode/bWV0YS10b2tlbi0x`

### Step 5: /meta_decode/bWV0YS10b2tlbi0x
- **Status**: 302
- **Cookies**: `visited_js=1` (carried forward)
- **Referer sent**: `https://web100-4.pointeroverflowctf.com/step_meta/bWV0YS10b2tlbi0x`
- **Location header**: `meta-token-1` (relative URL)
- **Resolves to**: `/meta_decode/meta-token-1`
- **Next URL**: `/meta_decode/meta-token-1`

### Step 6: /meta_decode/meta-token-1 ❌
- **Status**: 400
- **Response**: "Invalid payload"
- **Cookies**: `visited_js=1` (carried forward)
- **Referer sent**: `https://web100-4.pointeroverflowctf.com/meta_decode/bWV0YS10b2tlbi0x`

## Assumptions Made

1. **Redirect Chain Assumption**: Assumed the correct path is:
   - `/` → `/start` → `/step_js` → `/step_meta/bWV0YS10b2tlbi0x` → `/meta_decode/bWV0YS10b2tlbi0x` → `/meta_decode/meta-token-1`

2. **Base64 Decoding**: Assumed that the JavaScript double-decode attempt is intentionally failing, and only single decode should be applied at that step.

3. **Cookie Handling**: Assumed `visited_js=1` cookie needs to be preserved across all requests (which it was).

4. **Referer Chain**: Assumed each request should have Referer set to the previous URL in the chain (which it did).

5. **User-Agent**: Assumed standard browser User-Agent is sufficient.

6. **URL Resolution**: Assumed relative URLs should be resolved using urllib.parse.urljoin().

## Attempts Made

### 1. Python Script with requests library
- Implemented full redirect chain following
- Preserved cookies using requests.Session()
- Sent proper Referer headers
- Handled HTTP redirects, meta refresh tags, and JavaScript redirects
- Decoded Base64 payloads
- **Result**: 400 Invalid payload

### 2. Playwright Browser Automation
- Let real browser follow the chain
- **Result**: Also ended at 400 Invalid payload

### 3. curl with manual cookie management
- Followed chain step by step with curl
- Preserved cookies in cookie jar
- **Result**: 400 Invalid payload

### 4. Alternative Paths Tested
- Tried visiting `/step_meta/meta-token-1` (decoded version) instead of encoded
  - **Result**: Still led to 400 error
- Tried skipping intermediate steps
  - **Result**: 400 or 403 errors
- Tried common flag endpoints: `/final`, `/flag`, `/end`, `/complete`, `/success`
  - **Result**: All 404 Not Found

### 5. Different Decoding Approaches
- Tried double-decoding the JavaScript payload manually
- Tried decoding path components individually
- **Result**: No improvement

### 6. User-Agent Variations
- Tested with Mozilla, curl, and python-requests User-Agents
- **Result**: Same 400 error for all

### 7. Response Analysis
- Checked all HTTP headers for hidden data: None found
- Scanned all response bodies for hidden base64 strings: Only expected ones found
- Checked for hidden links in HTML: None that differ from Location headers
- Verified all cookies are being sent correctly: Confirmed

### 8. Testing `/final` Endpoint (New Attempt)
- Discovered `/final` endpoint exists and returns 400 "Incomplete final request"
- Tried accessing `/final` after various steps in the redirect chain
- Tried with query parameters (`?token=`, `?payload=`)
- Tried with custom headers (`X-Token`, `X-Payload`)
- Tried POST requests with form data
- Tried setting additional cookies (`token=`, `payload=`, `meta-token-1=`)
- **Result**: Always returns "Incomplete final request"

### 9. Systematically Testing Multiple Token Numbers (New Attempt)
- Tested `meta-token-1` through `meta-token-50` systematically
- Each token follows the same pattern:
  - `/step_meta/[base64-encoded-token]` returns 200 with meta refresh
  - `/meta_decode/[base64-encoded-token]` returns 302 redirect
  - `/meta_decode/[decoded-token]` returns 400 "Invalid payload"
- Also tested special values: `meta-token-0`, `meta-token` (no number), `meta-token-final`, `meta-token-100`
- **Result**: All tokens 0-50 give 400 errors at the final step

### 10. Visiting Tokens in Sequence (New Attempt)
- Tried visiting tokens 1-10 sequentially, checking if state accumulates
- Checked if visiting multiple tokens sets additional cookies: No
- Tried accessing `/final` after each token visit: Still "Incomplete final request"
- **Result**: No state accumulation observed, same errors

### 11. Deep HTML/Content Analysis (New Attempt)
- Parsed all responses for HTML comments: None found
- Checked for hidden form fields: None
- Looked for `data-*` attributes: None
- Checked for hidden elements (display:none, etc.): None
- Analyzed base tags and non-standard attributes: None found
- **Result**: No hidden breadcrumbs discovered in HTML

### 12. Testing Different Referer Combinations at Final Step (New Attempt)
- Tried all previous URLs in the chain as Referer for final step
- Tried relative Referers
- Tried no Referer header
- **Result**: All combinations give 400 error

### 13. Alternative Endpoint Discovery (New Attempt)
- Tested common endpoint patterns: `/flag`, `/admin`, `/complete`, `/success`, `/done`, `/finish`, `/end`, `/result`, `/solution`, `/answer`, `/token`, `/tokens`
- **Result**: All return 404 Not Found

## Questions/Uncertainties

1. **Is the challenge broken?** The server responds correctly to all steps until the final one, suggesting it's operational.

2. **Is there a missing step?** All intermediate responses point to the next step in a clear chain.

3. **Is the payload "meta-token-1" correct?** It comes from decoding `bWV0YS10b2tlbi0x` which is explicitly shown in step 4.

4. **Is there a timing component?** No indication of this in the challenge description or responses.

5. **Are there additional cookies needed?** Only `visited_js=1` is ever set by the server.

6. **Is the Referer chain incorrect?** Tested various Referer combinations with no success.

7. **Is there content after the 400 error?** Checked for hidden redirects or encoded content in the 400 response - none found.

## Files Created

### Main Scripts
- `redirect_follower.py`: Automated script to follow the redirect chain with detailed logging
- `follow_full_token_chain.py`: Systematically test tokens 1-50 through complete redirect chains

### Analysis Scripts
- `scan_responses.py`: Scan all responses for base64 strings
- `check_all_headers.py`: Display all HTTP headers from each step
- `check_links.py`: Extract all HTML links from responses
- `inspect_step3_detail.py`: Detailed inspection of JavaScript step
- `inspect_step4.py`: Detailed inspection of meta refresh step
- `inspect_step5.py`: Detailed inspection of meta_decode step
- `inspect_400_response.py`: Analyze the 400 error response
- `deep_inspect_step5.py`: Look for hidden HTML comments, attributes, etc.
- `check_400_cookies.py`: Check if 400 response sets cookies

### Testing Scripts
- `test_decoded_path.py`: Try decoded path variations
- `test_referers.py`: Test different Referer header combinations
- `test_alternatives.py`: Try token as query param, header, POST data
- `explore_final.py`: Investigate the `/final` endpoint
- `test_final_after_error.py`: Try `/final` after getting 400 error
- `try_final_after_redirect.py`: Try `/final` instead of following redirect
- `test_token_as_cookie.py`: Use meta-token-1 as cookie value
- `explore_more_tokens.py`: Test meta-token-2, 3, 4, etc.
- `follow_token2_chain.py`: Follow the chain for meta-token-2
- `find_working_token.py`: Test tokens 1-20 to find one that works
- `visit_tokens_in_sequence.py`: Visit multiple tokens sequentially
- `test_final_with_token.py`: Try `/final/meta-token-1`
- `try_special_tokens.py`: Test special token values (0, 100, final, etc.)
- `try_skipping_redirect.py`: Skip redirect and go to `/final`
- `check_redirect_destinations.py`: Check if any token redirects unexpectedly
- `test_endpoints.sh`: Test common endpoint patterns

## Next Steps for Someone Else

1. **Check if challenge is currently active**: The server may have been taken down or the flag changed.

2. **Review challenge hints**: There may be additional hints or updates on the CTF platform.

3. **Try with a different network**: Some challenges check source IP or network properties.

4. **Check for race conditions**: Maybe rapid requests in sequence behave differently?

5. **Look for alternative encoding**: Perhaps "meta-token-1" needs to be encoded differently (hex, URL encoding, etc.) before being sent?

6. **Check server-side timestamp**: Maybe the payload needs to include a timestamp or token from an earlier response?

7. **Review werkzeug/Flask documentation**: The server is running Werkzeug 3.1.3 - maybe there's a specific behavior or quirk?

## Tools/Scripts Available

All scripts are in the challenge directory and can be run with:
```bash
~/anaconda3/bin/conda run -n ctf python3 <script_name>.py
```

The main `redirect_follower.py` script is well-documented and can be modified to test different approaches.
