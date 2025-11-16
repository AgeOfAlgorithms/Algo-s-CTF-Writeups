## Challenge Name
Two Wrongs Make a Right

## Platform
UWSP Pointer Overflow CTF 2025

## Category
Crypto

## Difficulty
medium

## Challenge Description
Two ciphertexts were produced with CTR mode using the same nonce and same key (keystream reuse). Recover both plaintexts. You are given two ciphertexts (hex) and the nonce. The key is unknown. You have recieved a leak of the C1 plaintext, found below:

"""From: Tamsin To: Mason Date: Sat, 11 Oct 2025 10:02:05 -0500 Subject: System checks and handoff plan

Hey—quick handoff notes before I go off-grid: • Rotate the service tokens on barad-dur first, then traefik. • The staging login banner still shows "2024"; fix that. • If anyone pings you about CRYP 200-1, tell them it's not a padding-oracle. • Also: the validator only accepts lowercase flags.

Final reminder: never ship secrets in plaintext. Use proper key management and never reuse a CTR nonce again.

—T """

Remember: For CTR, C = P ⊕ KS. If two messages reuse the same nonce/key, they share the same keystream KS. Therefore C1​⊕C2​=(P1​⊕KS)⊕(P2​⊕KS)=P1​⊕P. Use crib-dragging with likely English fragments to peel back each message.

[attachment](crypto200-1)
