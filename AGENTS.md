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
- Never commit or push visual or functional changes until the product owner has
  reviewed them locally and explicitly authorizes the commit or push.
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
- The Audio Chopper uses a reusable browser component for direct selection,
  mouse-wheel zoom/navigation, synchronized playback, looping, edge auto-pan,
  listening-only Monitor Level, and fade audition without Streamlit reruns.
  `Use Selection` must trim immediately through the authoritative Python/FFmpeg
  path and load the first free slot. Saved clips live only in the temporary
  four-slot LCD Sample Memory, share one compact browser player, and download
  together as a ZIP. Direct background drag-to-pan remains a future enhancement.
- The Stereo / Mono Converter is a focused Transform tool. Keep channel probing,
  validation, bitrate policy, splitting, interleaving, and silence-padding in
  reusable engine/product modules rather than the page. WAV is the lossless
  option; MP3 Match Source must not claim that a higher bitrate restores quality.
- Audio Format Converter is a focused Transform tool backed by
  `format_converter.py` and the shared FFmpeg engine. It supports MP3, WAV PCM,
  FLAC, M4A/AAC, and ALAC. Match Source must preserve sample rate where possible;
  upsampling or a higher lossy bitrate must never be presented as restored quality.
- Delay & Reverb Calculator is an instant TOOLS utility with no upload or server
  audio processing. Keep timing formulas in `timing_calculator.py`; the v3 Sync
  Generator owns browser audio, Tap Tempo, BPM gestures, subdivisions, and its
  4/8/16/32-step display. Reverb results are starting points, not fixed rules.
- The Mastering Analyzer is a focused Analyze tool. Keep LUFS,
  peak/true-peak, dynamic-range, stereo-width, phase-correlation, and mono
  compatibility measurements in reusable analysis modules rather than the page.
- Present mastering measurements with their units, measurement method, and
  limitations. Do not reduce mastering quality to a single unexplained score.
- Keep A/B comparison measurements based on the original uploaded masters.
  Volume Match may alter temporary listening copies only and must be optional.
- The comparison flow uses a lightweight synchronized browser-side A/B deck,
  not two copies of the full single-master monitor. Keep both sources on the
  same playhead while allowing only the selected A or B source to reach the
  output. Global LUFS/RMS bars must use the authoritative original-file report;
  live RMS markers may follow the current listening copies. A/B Monitor Level
  and Mute must remain after source selection and affect listening only.
- The single-master flow uses a reusable browser-side Web Audio player for its
  waveform, playhead, spectrum, analog Peak/RMS meters, digital L/R Peak/RMS
  bars with Peak Hold, stereo vectorscope, unified balance/width/phase display,
  response speed, Mono Check, and listening-only Monitor Level. The Monitor
  Level and Mute must remain after the measurement taps so they never affect
  live meter values or authoritative analysis. Streamlit reruns must not drive
  live meters or playback synchronization.
- Treat live browser measurements as responsive listening context, not final
  report values. Keep FFmpeg analysis authoritative for integrated LUFS, true
  peak, dynamics, static stereo/spectral measurements, and the final mastering
  report. A future spectrogram and live short-term/momentary LUFS must state
  their method and limitations.
- The Speed Changer uses a reusable browser-side Live Speed Deck for waveform,
  playback, live BPM/speed changes, Follow Speed, and Keep Original Pitch.
  Custom Pitch uses an accessible analog knob; its accurate 20-second preview
  and all final exports remain authoritative on Python/FFmpeg. New uploads must
  start with Target BPM equal to detected Original BPM at `1.000×`; correcting
  Original BPM should also restore neutral speed. Monitor Level and Mute affect
  browser listening only and must never enter preview or export settings. The
  v3 deck locks Original BPM by default; Reset to Detected BPM restores the
  initial detection, Target BPM, `1.000×`, Follow Speed, and zero custom pitch.
- Keep product analytics centralized and optional. Never send uploaded audio,
  filenames, raw cookies, IP addresses, or other unnecessary personal data.
- Keep public feedback account-free and rate-limited. Submit only the category,
  rating, and message the visitor intentionally provides; never attach audio or
  filename metadata automatically.
- Load the shared Jungle Analog design once in `app.py`, immediately after
  `st.set_page_config`. Individual pages must not call `load_design()` again.
- Keep the lightweight Jungle Analog CSS separate from large embedded artwork so
  typography and controls can render before the background image is decoded.
- Streamlit Cloud's authenticated static-asset route proved unreliable for CSS
  backgrounds. The current background and home hero are embedded as data URIs
  from versioned files in `static/`; do not switch them back to public URLs
  without verifying the deployed application.
- Version the Streamlit v2 waveform component name and key when its browser-side
  HTML, CSS, or JavaScript changes. This prevents a deployed browser from
  retaining an older component bundle.
- Apply the same name/key versioning rule to the Speed Deck and Mastering
  Monitor whenever their HTML, CSS, or JavaScript changes.
- Never place user filenames directly in Streamlit v2 component keys. Streamlit
  reserves `__` inside bidirectional IDs, and downloaded files commonly contain
  that sequence. Use `safe_component_key()` for any user-derived component key
  or browser audio identity while keeping the original name visible to users.

## Current application structure

- `app.py`: application entry point and multipage navigation.
- `audio_analysis.py`: key, BPM, and Camelot analysis logic.
- `audio_engine.py`: reusable FFmpeg runner and processing errors.
- `audio_effects.py`: reusable product-level audio transformations.
- `audio_chopper.py`: waveform extraction and selected-fragment export.
- `waveform_component.py`: browser-side interactive waveform and playback.
- `sample_tray_component.py`: compact browser-side four-slot Sample Memory.
- `stereo_converter.py`: product-level channel-routing and export policy.
- `format_converter.py`: product-level codec, bitrate, depth, and sample-rate policy.
- `timing_calculator.py`: reusable tempo-derived delay and reverb formulas.
- `sync_generator_component.py`: browser-side tempo clock and claquette.
- `component_keys.py`: deterministic filename-safe Streamlit component keys.
- `speed_player_component.py`: browser-side live Speed Changer deck and analog
  pitch controls.
- `mastering_analysis.py`: loudness, stereo, and static spectral analysis.
- `mastering_monitor_component.py`: browser-side live mastering player,
  spectrum, meters, stereo readouts, and Mono Check.
- `mastering_ab_component.py`: lightweight synchronized A/B player, instant
  source switching, LUFS/RMS comparison bars, live RMS markers, and listening
  Monitor Level.
- `stem_separation.py`: product-level local and cloud vocal separation.
- `cloud_stem_separation.py`: private Modal vocal separation client.
- `modal_vocal_split_server.py`: private zero-retention Modal GPU server.
- `analytics.py`: optional privacy-conscious product-event tracking.
- `feedback.py`: feedback validation, delivery, and public contact settings.
- `ui.py`: shared Streamlit presentation helpers.
- `static/`: versioned jungle background and homepage bird/laboratory artwork.
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
  original pitch, independent pitch adjustment, and live browser audition. Keep
  the rendered server preview only for Custom Pitch, where browser playback
  cannot accurately reproduce independent pitch and tempo processing.
- Vocal Split supports a selectable local 20-second preview, and its private
  Modal GPU processing service is being connected to the application.
- Keep pitch and tempo processing reusable so future focused, SEO-friendly tool
  pages can share the same engine without duplicating logic.
- Audio Chopper provides a high-resolution interactive waveform, direct
  range selection, mouse-wheel and button zoom, horizontal and edge-triggered
  navigation, synchronized playhead, Loop Selection, listening-only Monitor
  Level, and live edge-fade audition. `Use Selection` immediately creates the
  authoritative FFmpeg sample in the first free slot. The compact four-slot LCD
  Sample Memory supports inline rename, shared playback, removal, and ZIP
  download without native per-sample audio players.
- Stereo / Mono Converter provides explicit Stereo → L Mono + R Mono and
  L Mono + R Mono → Stereo flows. It supports WAV/MP3, Match Source plus
  128/192/256/320 kbps, Swap L/R, visible silence-padding behavior, result
  monitoring, separate/ZIP downloads, and a restrained analog patch-bay diagram.
- Audio Format Converter provides Source Reel → Format Matrix → Output Reel
  conversion for MP3, WAV, FLAC, M4A/AAC, and ALAC. It exposes Match Source,
  128/192/256/320 kbps, 16/24/32-bit WAV, supported studio sample rates, preview,
  and download while explaining lossy re-encoding and upsampling limitations.
- The Mastering Analyzer now provides LUFS, dBFS/true peak, dynamics, stereo
  measurements, mono compatibility, A/B reference comparison, Volume Match,
  static spectral balance, and a live single-master Web Audio monitor. The live
  monitor has waveform seeking, spectrum, illuminated analog Peak/RMS meters,
  full-height digital L/R Peak/RMS bars with Peak Hold, a stereo vectorscope,
  unified balance/width/phase and mono-safety visualization, Mono Check,
  listening-only Monitor Level/Mute, and Steady/Balanced/Fast response. Keep it
  distinct from any future AI Mastering product.
- The comparison mode uses the v2 synchronized A/B deck. It starts both audio
  sources at one shared playhead, routes only A or B to the output, corrects
  meaningful playback drift, supports Original and Volume Match listening, and
  shows authoritative global LUFS/RMS beside live RMS markers. Its Monitor
  Level/Mute is downstream of A/B selection and cannot alter measurements.
- Delay & Reverb Calculator is one focused TOOLS page that works instantly from
  BPM without an upload. Reverb starting points appear before the complete delay
  bank. Its Sync Generator v3 supports typing, plus/minus, wheel, vertical drag,
  Tap Tempo, detailed straight/dotted/triplet clicks through 1/32, and selectable
  4/8/16/32-step cycles.
- Defer accounts, subscriptions, billing, and persistent user files until their
  product and infrastructure requirements are designed.

## Current handoff state

- Public navigation is grouped into HOME, ANALYZE, TRANSFORM, SEPARATE, TOOLS,
  and SUPPORT. The live tools are Key & BPM Finder, Speed Changer, Mastering
  Analyzer, Audio Chopper, Stereo / Mono Converter, Audio Format Converter,
  Delay & Reverb Calculator, and Feedback.
- The shared visual direction is **Jungle Analog**: a sophisticated analog audio
  laboratory hidden in a humid jungle around 1975–1985. Use Jungle Night/Deep
  Forest, walnut, oxidized metal, Old Paper/Warm Cream, olive/moss, and VU Amber.
  Controls should feel tactile and equipment-inspired while remaining modern,
  clean, responsive, and immediately understandable.
- Acid Lime, neon borders, glow-heavy controls, glassmorphism, cyberpunk, generic
  AI SaaS gradients, tiki/resort imagery, steampunk, and fake terminal interfaces
  are not part of the current identity. The two neon lights already painted into
  the original homepage bird/laboratory illustration are the only intentional
  neon exception.
- Preserve both original embedded artworks: the full jungle-leaf application
  background and the homepage bird/scientist analog-laboratory hero. Do not
  replace either with CSS-only artwork. Warm overlays may improve readability,
  but the underlying images must remain visible.
- Use local/system typography rather than late-loading Google Fonts to avoid a
  font swap during initial render. The compact `VIBES SUPPLIER` and
  `VS / AUDIO SYSTEM` equipment-label language is the current identity, while
  the product name remains provisional.
- Shared buttons use tactile 1980s equipment styling, physical pressed states,
  subtle texture, and amber processing lamps. Live processing states should
  resemble equipment powering on rather than neon software loading.
- The Audio Chopper component currently uses the v10 component name/key. Its
  fixed height is 390 px so its waveform, fade selector, Monitor Level, and
  accessible navigation controls are not clipped on Streamlit Cloud. The LCD
  Sample Memory uses its own v1 component name/key.
- The Speed Changer Live Deck currently uses the v3 component name/key. It
  starts at the detected BPM and `1.000×`, resets Target BPM to a manually
  corrected Original BPM, locks Original BPM against accidental edits, restores
  all neutral detected settings on reset, and includes listening-only Monitor
  Level/Mute that cannot affect preview or export processing.
- The Mastering Monitor currently uses the v10 component name/key. Its live
  spectrum and vectorscope remain fluid while the user selects Steady,
  Balanced, or Fast meter response. Its Peak/RMS meters use restrained black
  oxidation, warm glass, incandescent illumination, and correctly positioned
  VU scales. Full-height digital L/R bars show Peak, RMS, Peak Hold, and
  clipping. Balance, width, and phase/mono safety share one instrument panel,
  including visible phase-cancellation risk. Monitor Level and Mute affect
  listening only and remain downstream of all measurement taps.
- Vocal Split's 20-second Modal preview was quality-validated, but public use is
  paused because isolated requests were approximately $0.017-$0.020 with the
  current idle window. `ECONOMY.md` contains the assumptions and benchmarks.
- PostHog is configured through Streamlit secrets and currently records page
  views plus explicit feedback submissions. Analytics must remain optional and
  must never receive audio, filenames, raw cookies, or location data.
- The public feedback contact is `vibes.supplier@gmail.com`.
- Mastering Monitor, Mastering A/B, and Speed Deck use hashed internal audio
  identities so filenames containing `__`, Unicode, emoji, or punctuation never
  enter Streamlit v2 IDs. Audio Chopper already uses fixed component keys.
- The current automated suite contains 89 tests and passes with
  `.venv/bin/python -m unittest discover -s tests -q`. The local virtual
  environment does not currently include pytest.

## Recommended next session

1. Verify the deployed Delay & Reverb Calculator timing, BPM gestures, click
   subdivisions, and 4/8/16/32-step layout on desktop and mobile.
2. Choose one focused increment: Audio Chopper drag-to-pan or a new producer utility.
3. Keep the increment small, run the 89-test suite, syntax and diff checks, then
   wait for explicit product-owner approval before committing or pushing.
