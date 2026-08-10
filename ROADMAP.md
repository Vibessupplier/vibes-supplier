# 🚀 Audio Tool Roadmap

## Version 0.1
- [x] Upload audio
- [x] Audio player
- [x] Key detection
- [x] BPM detection
- [x] Camelot conversion
- [x] Alternative key detection
- [x] Multipage navigation
- [x] Initial dark UI
- [x] Initial provisional neon logo
- [x] Replace the provisional neon identity with the Jungle Tech visual system
- [x] Jungle Tech homepage and tool-family navigation
- [x] Shared typography, sidebar, cards, controls, and responsive styling
- [x] Dark tropical background and homepage hero artwork
- [x] Load shared styling before page content to reduce old-theme flashes
- [x] Evolve Jungle Tech into the warm Jungle Analog visual system
- [x] Analog equipment panels, tactile controls, amber lamps, and meters

---

## Version 0.2
- [x] Reusable FFmpeg audio engine
- [x] Speed Changer page
- [x] Exact target BPM control
- [x] Nightcore-style speed up (covered by Speed Changer)
- [x] Slowed-style speed down (covered by Speed Changer)
- [x] Pitch follows speed mode
- [x] Preserve original pitch mode
- [x] Independent Pitch Shifter (-12 to +12 semitones)
- [x] Independent Tempo Changer
- [x] MP3 export and download
- [x] 20-second rendered preview for independent Custom Pitch
- [x] Invalidate preview when speed or pitch changes
- [x] Improve Speed Changer controls and player UI
- [x] Live browser-side Speed Changer deck with waveform and playhead
- [x] Start live audition at the detected BPM and neutral `1.000×` speed
- [x] Listening-only Speed Deck Monitor Level and Mute
- [x] Audition Follow Speed and Keep Original Pitch without server previews
- [x] Accessible analog Custom Pitch knob

---

## Version 0.3
- [x] Local Vocal Split prototype
- [x] Acapella and instrumental players and downloads
- [x] Validate Demucs separation quality with a full track
- [x] Select the start point for a free 20-second Vocal Split preview
- [x] Process only the selected preview segment
- [ ] Compare clean and natural acapella separation modes
- [x] Run Vocal Split processing on Modal GPU
- [ ] Re-enable the public preview after access and cost controls are ready
- [ ] Add background processing and temporary result delivery

---

## Version 0.4
- [x] Privacy-conscious PostHog page and product-event analytics
- [x] Public Feedback page with rating, category, message, and contact email
- [x] International-facing presentation without Barcelona/location references
- [x] Public contact address: vibes.supplier@gmail.com
- [ ] Producer accounts
- [ ] Monthly subscription with processing credits
- [ ] Free Vocal Split previews
- [ ] Premium full-track Vocal Split
- [ ] Stripe subscription checkout and billing management
- [ ] Usage limits and cost monitoring
- [ ] Free users: MP3 export only
- [ ] Premium users: WAV, FLAC, and additional high-quality export formats
- [ ] Apply the free and Premium format policy consistently across audio tools

---

## Future Vocal Tools
- [ ] Vocal Mode
- [ ] Vocal Range Detector
- [ ] Pitch Correction Preset Generator

---

## Future Analyze Tools
- [x] Mastering Analyzer page
- [x] Integrated LUFS measurement
- [ ] Short-term and momentary LUFS measurements
- [x] Peak and true-peak level measurements in dBFS/dBTP
- [x] Loudness range and RMS level indicators
- [ ] Additional dynamic-range indicators
- [x] Static stereo balance, width, phase correlation, and mono compatibility
- [x] Clear mastering-oriented result summaries and measurement explanations
- [x] A/B mastering comparison against a user-selected reference track
- [x] Optional non-destructive Volume Match for reference listening
- [ ] Configurable mastering reference ranges
- [x] Static spectral balance visualization and A/B comparison
- [x] Label Sub, Bass, Low Mid, Mid, High Mid, and High frequency ranges
- [x] Custom synchronized audio player for the single Mastering Analyzer
- [x] Interactive waveform with clickable playhead
- [ ] Live spectrogram
- [x] Live peak and RMS meters with selectable response speed
- [x] Illuminated analog Peak/RMS meters with correctly positioned VU scales
- [x] Full-height digital L/R Peak, RMS, clipping, and Peak Hold meters
- [ ] Live momentary and short-term LUFS meters
- [x] Live frequency spectrum, stereo balance, and phase correlation meters
- [x] Live stereo vectorscope/goniometer
- [x] Unified visual Balance, Width, and Phase/Mono Safety instrument
- [x] Phase-cancellation risk zones and live mono-safety status
- [x] Listening-only Monitor Level and Mute that do not affect measurements
- [x] Browser-side Mono Check for temporary listening
- [x] Lightweight synchronized A/B listening deck with instant source switching
- [x] Original/Volume Match listening, global LUFS/RMS bars, and live RMS markers
- [x] Listening-only A/B Monitor Level and Mute after source selection
- [ ] Highlight clipping and notable loudness sections on the timeline

---

## Future Ideas
- [x] Audio Chopper page
- [x] High-resolution waveform data and precise sample trimming
- [x] Browser-side original-track and selected-fragment audition
- [x] Export user-selected samples in MP3
- [x] JavaScript/Web Audio waveform component with direct drag selection
- [x] Mouse-wheel zoom and horizontal navigation without Streamlit reruns
- [x] Accessible zoom and horizontal navigation buttons for trackpads and touch users
- [x] Synchronized playhead and infinite Loop Selection mode
- [x] Visible confirmation when applying a waveform selection
- [x] `Use Selection` immediately exports through FFmpeg into the first free slot
- [x] Reusable selection after creating or removing a sample
- [x] Compact four-slot LCD Sample Memory with rename, play/stop, progress, and remove actions
- [x] Listening-only Monitor Level and Mute that never affect sample export
- [x] Automatic edge navigation while dragging a zoomed selection
- [x] Optional 5/10/25/50 ms edge fades, auditioned live and rendered authoritatively by FFmpeg
- [x] Download all saved samples together as `vibes_supplier_samples.zip`
- [ ] Direct drag-to-pan waveform navigation
- [ ] Premium WAV and FLAC sample export
- [x] Stereo / Mono Converter standalone page
- [x] Split a stereo source into independent lossless L and R mono files
- [x] Interleave two mono sources as assigned L/R channels in one stereo file
- [x] WAV and MP3 output with Match Source and 128/192/256/320 kbps selection
- [x] Preserve sample rate and PCM bit depth for compatible lossless exports
- [x] Warn clearly when lossy formats require re-encoding
- [x] Preview L/R routing, swap channel assignment, and download split files together
- [x] Handle unequal mono durations explicitly, with visible silence-padding behavior
- [ ] Universal audio format converter for WAV, MP3, FLAC, M4A, and additional formats
- [ ] Multi-stem separation (vocals, drums, bass, and other)
- [ ] Spectrogram
- [ ] AI Mix Assistant
- [ ] AI Mastering

---

## Future Timing Calculators

- [ ] Delay Time Calculator page
- [ ] Convert BPM into milliseconds for whole, half, quarter, eighth, and
  sixteenth-note delays
- [ ] Include dotted and triplet delay subdivisions
- [ ] Present left/right and ping-pong timing combinations without prescribing
  a single creative setting
- [ ] Reverb Time Calculator page
- [ ] Convert BPM and rhythmic subdivisions into useful pre-delay starting
  points
- [ ] Suggest tempo-synchronized decay ranges for short, medium, and long
  spaces
- [ ] Explain that reverb timings are starting points shaped by arrangement,
  genre, source material, and creative intent
- [ ] Keep both calculators instant and browser-friendly without requiring an
  audio upload

---

## Next Product Increments

- [ ] Validate Jungle Analog initial loading and embedded artwork on Streamlit Cloud
- [ ] Test the complete public flow on desktop and mobile
- [ ] Validate Stereo / Mono Converter routing, formats, ZIP, and patch-bay layout online
- [ ] Add Audio Chopper direct drag-to-pan navigation
- [ ] Build the Delay Time Calculator as a focused standalone tool
- [ ] Define and validate the Reverb Time Calculator formulas and guidance
- [ ] Validate the synchronized A/B deck on desktop Edge and mobile browsers
- [ ] Benchmark Modal with full three-minute MP3 and WAV tracks
- [ ] Define free and Premium usage limits from measured processing costs
- [ ] Prepare a small external beta and review PostHog and Feedback results

## Current Public Beta State

- Home, Key & BPM Finder, Speed Changer, Mastering Analyzer, Audio Chopper,
  Stereo / Mono Converter, and Feedback are available through the sidebar.
- Vocal Split works with a high-quality private Modal/Demucs pipeline, but its
  public processing action is intentionally disabled while cost and access
  controls are designed.
- Audio Chopper has direct waveform selection, wheel and button zoom,
  horizontal and automatic edge navigation, synchronized playback, looping,
  listening-only Monitor Level, reusable one-click selection, optional edge
  fades, a compact four-slot LCD Sample Memory, and combined ZIP export.
- Stereo / Mono Converter splits stereo into discrete L/R mono files or
  interleaves two mono sources as stereo. It supports WAV and MP3, Match Source
  bitrate, advanced MP3 bitrates, Swap L/R, silence-padding for unequal lengths,
  individual/ZIP downloads, and a Jungle Analog routing patch bay.
- Speed Changer has a browser-side Live Speed Deck for instant tempo audition,
  Follow Speed, Keep Original Pitch, an analog Custom Pitch knob, and a
  listening-only Monitor Level/Mute. New uploads start with Target BPM equal to
  detected Original BPM at `1.000×`; correcting Original BPM also preserves
  neutral speed. Only Custom Pitch requires a rendered preview before final
  FFmpeg export.
- Mastering Analyzer Single Master has a live Web Audio monitor with waveform,
  spectrum, Mono Check, analog Peak/RMS meters, full-height digital L/R meters,
  vectorscope, unified stereo/phase visualization, selectable response, and a
  listening-only Monitor Level. The final global report remains authoritative
  on FFmpeg.
- Mastering Analyzer Compare has a lightweight synchronized A/B deck with one
  audible source at a time, instant A/B switching, Original or Volume Match
  playback, global original-file LUFS/RMS bars, live RMS markers, and a
  listening-only Monitor Level. It intentionally does not duplicate the full
  single-master laboratory.
- The active art direction is Jungle Analog. The original jungle background and
  bird/audio-laboratory hero remain core artwork; UI neon and Acid Lime were
  replaced by warm cream, walnut, oxidized metal, olive, and VU Amber.
- PostHog receives privacy-conscious page views and explicit feedback events.
- The application deploys automatically from `main` to Streamlit Community
  Cloud; a reboot is sometimes required before a new build becomes visible.
