# SAFETY — Total War: ATTILA Arabic POC

Game install is READ-ONLY:

`D:\SteamLibrary\steamapps\common\Total War Attila`

Rules (binding for all phases):

- NEVER overwrite, delete, rename, or modify vanilla files.
- NEVER modify original `.pack` files in place.
- NEVER modify original font files in place.
- NEVER patch or hex-edit `Attila.exe`.
- NEVER auto-edit `user.script.txt`
  (`%APPDATA%\The Creative Assembly\Attila\scripts\user.script.txt`).
  Mod enabling is via the launcher Mod Manager only.
- All analysis works on COPIES under `D:\AttilaArabic\extracted\`.
- The only game-directory write ever allowed is a TEMPORARY copy of the
  final standalone test `.pack` into the game's normal mod/data location
  for the Mod Manager test, removed afterwards.
- SHA256 hashes of source packs are recorded in `logs\baseline.txt`
  before and after testing to prove no vanilla file changed.

Workspace: `D:\AttilaArabic\` (all generated/modified files live here).
