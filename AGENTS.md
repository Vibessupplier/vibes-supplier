# Vibes Supplier — Project Instructions

## Product direction

- Build a maintainable SaaS platform of focused audio tools for producers, DJs,
  and artists.
- Treat the name "Vibes Supplier" as provisional.
- Do not use "Auto-Tune" or "AutoTune" as product branding because it is a
  third-party trademark.
- Each tool must have its own page and search-focused purpose. Do not combine
  every feature into one large page.

## Working style

- Treat the user as the product owner and the agent as the technical lead. Discuss
  product and architecture decisions instead of imposing them.
- The product owner is an experienced music producer but is new to programming.
  Never assume knowledge of Python, terminals, virtual environments,
  dependencies, classes, or software architecture.
- Explain important decisions in plain language and connect technical concepts
  to a concrete product benefit. Avoid detached programming lessons.
- Give honest technical and product feedback. Do not agree with an idea when it
  would damage maintainability, UX, security, SEO, or future scalability.
- Work in small, verifiable increments: objective, small change, test, commit,
  push.
- Finish and verify one feature before starting another.
- Prefer sessions that end with a visible, working product improvement.
- Prefer a durable design over a quick workaround.
- Challenge product or technical ideas that would create security,
  maintainability, UX, or scaling problems.
- Do not perform broad refactors unless they are required for the current
  increment and explained first.

## Architecture

- Keep Streamlit pages focused on presentation and user interaction.
- Keep audio analysis, transformations, and infrastructure outside the UI.
- Use `audio_engine.py` as the low-level FFmpeg execution layer.
- Use `audio_effects.py` for product-level transformations such as Nightcore.
- UI code must call product-level functions; it must not construct raw FFmpeg
  commands or filters.
- Use FFmpeg as the shared processing engine for pitch, tempo, format conversion,
  export, and related effects.
- Never invoke FFmpeg through `shell=True`. Pass command arguments as a list.
- Validate user-controlled values before passing them to the processing layer.
- Use temporary storage for uploaded and generated audio. Do not retain user
  audio after processing unless persistent storage is intentionally designed.
- Keep waveform selection in the UI, but perform sample extraction and export
  through reusable product-level functions backed by `audio_engine.py`.
- The Audio Chopper uses a reusable JavaScript/Web Audio component for direct
  selection, mouse-wheel zoom/navigation, synchronized playback, and looping
  without Streamlit reruns. Keep final trimming and export authoritative on
  the Python/FFmpeg side; direct drag-to-pan remains a future enhancement.
- Build the future Mastering Analyzer as a focused Analyze tool. Keep LUFS,
  peak/true-peak, dynamic-range, stereo-width, phase-correlation, and mono
  compatibility measurements in reusable analysis modules rather than the page.
- Present mastering measurements with their units, measurement method, and
  limitations. Do not reduce mastering quality to a single unexplained score.
- Keep A/B comparison measurements based on the original uploaded masters.
  Volume Match may alter temporary listening copies only and must be optional.
- Build future live Mastering Analyzer visuals as a reusable browser-side audio
  player component backed by the Web Audio API. Streamlit reruns must not drive
  real-time meters or playback synchronization.
- Keep the browser player responsible for waveform, spectrogram, playhead, and
  responsive live meters. Keep FFmpeg analysis as the authoritative source for
  final LUFS, peak, and mastering-report measurements.
- Keep product analytics centralized and optional. Never send uploaded audio,
  filenames, raw cookies, IP addresses, or other unnecessary personal data.
- Keep public feedback account-free and rate-limited. Submit only the category,
  rating, and message the visitor intentionally provides; never attach audio or
  filename metadata automatically.
- Load the shared Jungle Tech design once in `app.py`, immediately after
  `st.set_page_config`. Individual pages must not call `load_design()` again.
- Keep the lightweight Jungle Tech CSS separate from large embedded artwork so
  typography and controls can render before the background image is decoded.
- Streamlit Cloud's authenticated static-asset route proved unreliable for CSS
  backgrounds. The current background and home hero are embedded as data URIs
  from versioned files in `static/`; do not switch them back to public URLs
  without verifying the deployed application.
- Version the Streamlit v2 waveform component name and key when its browser-side
  HTML, CSS, or JavaScript changes. This prevents a deployed browser from
  retaining an older component bundle.

## Current application structure

- `app.py`: application entry point and multipage navigation.
- `audio_analysis.py`: key, BPM, and Camelot analysis logic.
- `audio_engine.py`: reusable FFmpeg runner and processing errors.
- `audio_effects.py`: reusable product-level audio transformations.
- `audio_chopper.py`: waveform extraction and selected-fragment export.
- `waveform_component.py`: browser-side interactive waveform and playback.
- `mastering_analysis.py`: loudness, stereo, and static spectral analysis.
- `stem_separation.py`: product-level local and cloud vocal separation.
- `cloud_stem_separation.py`: private Modal vocal separation client.
- `modal_vocal_split_server.py`: private zero-retention Modal GPU server.
- `analytics.py`: optional privacy-conscious product-event tracking.
- `feedback.py`: feedback validation, delivery, and public contact settings.
- `ui.py`: shared Streamlit presentation helpers.
- `static/`: versioned Jungle Tech background and homepage hero artwork.
- `pages/`: independent Streamlit tool pages.
- `tests/`: automated tests.
- `requirements.txt`: Python dependencies for local and cloud environments.
- `packages.txt`: system packages required by Streamlit Community Cloud.

## Quality rules

- Preserve existing working behavior unless the current task explicitly changes
  it.
- Add or update tests for processing behavior and regressions.
- Run the relevant automated tests before committing.
- Run Python syntax checks and `git diff --check` before committing.
- Keep commits small and focused on one working increment.
- Do not commit generated audio, temporary files, secrets, credentials, virtual
  environments, or Python cache files.
- Do not add a production dependency without explaining why it is needed.

## Deployment

- The application deploys from the `main` branch to Streamlit Community Cloud.
- Remember that local Homebrew packages are not available in the cloud;
  required Debian packages belong in `packages.txt`.
- A successful local test does not replace checking the Streamlit deployment
  logs and the published user flow after pushing.
- Streamlit Community Cloud can continue displaying the previous deployment
  until its new build is ready. Reboot only after checking that `main` contains
  the intended commit, and use a hard browser refresh when validating visual or
  JavaScript component changes.
- Large embedded artwork must be injected after the lightweight global CSS. A
  brief Jungle Black/Deep Forest loading state is acceptable; flashing the old
  neon/default interface is not.

## Near-term direction

- Nightcore-style and Slowed-style transformations are now modes of the shared
  Speed Changer rather than separate duplicated processing engines.
- The Speed Changer supports exact target BPM, pitch following speed, preserved
  original pitch, and independent pitch adjustment.
- Vocal Split supports a selectable local 20-second preview, and its private
  Modal GPU processing service is being connected to the application.
- Keep pitch and tempo processing reusable so future focused, SEO-friendly tool
  pages can share the same engine without duplicating logic.
- Audio Chopper Beta provides a high-resolution interactive waveform, direct
  range selection, mouse-wheel and button zoom, horizontal navigation buttons,
  synchronized playhead, Loop Selection, visible Use Selection confirmation,
  optional processed preview, and MP3 export. Browser interaction must reuse the
  existing trimming engine rather than duplicate final export processing inside
  the component.
- The Mastering Analyzer now provides LUFS, dBFS/true peak, dynamics, stereo
  measurements, mono compatibility, A/B reference comparison, Volume Match,
  and static spectral balance. Keep it distinct from any future AI Mastering
  product.
- Defer accounts, subscriptions, billing, and persistent user files until their
  product and infrastructure requirements are designed.

## Current handoff state

- Public navigation is grouped into HOME, ANALYZE, TRANSFORM, SEPARATE, and
  SUPPORT. The live tools are Key & BPM Finder, Speed Changer, Mastering
  Analyzer, Audio Chopper Beta, and Feedback.
- The shared visual direction is "Jungle Tech": Jungle Black/Deep Forest
  surfaces, Bone/Sand typography, restrained Acid Lime interactions, occasional
  Mango accents, and dark tropical artwork. Avoid generic cyberpunk, gaming,
  tourist/Hawaiian, and generic black-blue SaaS styling.
- The provisional old cyan neon wordmark is no longer the desired identity.
  The homepage hero and compact editorial `VIBES SUPPLIER` header are the current
  direction, while the product name itself remains provisional.
- Commit `0de0746` introduced two-stage visual loading: lightweight shared CSS
  first and the embedded jungle background second. Its purpose is to prevent the
  previous interface from flashing during reloads. Confirm this behavior on the
  deployed site before beginning a broad new feature.
- The Audio Chopper component currently uses the v4 component name/key. Its
  fixed height is 330 px so the accessible arrow and plus/minus controls are not
  clipped on Streamlit Cloud.
- Vocal Split's 20-second Modal preview was quality-validated, but public use is
  paused because isolated requests were approximately $0.017-$0.020 with the
  current idle window. `ECONOMY.md` contains the assumptions and benchmarks.
- PostHog is configured through Streamlit secrets and currently records page
  views plus explicit feedback submissions. Analytics must remain optional and
  must never receive audio, filenames, raw cookies, or location data.
- The public feedback contact is `vibes.supplier@gmail.com`.
- The current automated suite contains 44 tests and passes with
  `.venv/bin/python -m unittest discover -s tests -q`. The local virtual
  environment does not currently include pytest.

## Recommended next session

1. Verify the latest deployed visual loading behavior, Audio Chopper controls,
   and Use Selection confirmation on the public Streamlit URL.
2. If the old interface still flashes, diagnose Streamlit's retained DOM/loading
   behavior as a focused visual issue; do not undo the working Jungle Tech theme.
3. Choose one product increment: direct waveform drag-to-pan, live Mastering
   Analyzer visuals, or public-beta preparation and user testing.
4. Keep the increment small, run the 44-test suite, run syntax and diff checks,
   commit, push to `main`, and verify the deployed flow.
