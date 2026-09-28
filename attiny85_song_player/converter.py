import mido
import sys

# Set hard ceiling to 2500 notes (~5 KB Flash, perfectly fitting ATtiny85)
MAX_NOTES = 2500 

# Equal Temperament note frequencies (C3 to B5)
NOTE_LOOKUP = [
    0,   # 0: REST
    131, 139, 147, 156, 165, 175, 185, 196, 208, 220, 233, 247, # C3 - B3
    262, 277, 294, 311, 330, 349, 370, 392, 415, 440, 466, 494, # C4 - B4
    523, 554, 587, 622, 659, 698, 740, 784, 831, 880, 932, 988  # C5 - B5
]

def freq_to_idx(freq):
    if freq == 0:
        return 0
    best_idx = 1
    min_diff = abs(freq - NOTE_LOOKUP[1])
    for i in range(2, len(NOTE_LOOKUP)):
        diff = abs(freq - NOTE_LOOKUP[i])
        if diff < min_diff:
            min_diff = diff
            best_idx = i
    return best_idx

def convert_midi_monophonic(midi_path, output_h="song_data.h"):
    mid = mido.MidiFile(midi_path)
    events = []
    
    # Strip Channel 10 (Drums/Percussion)
    for track in mid.tracks:
        abs_time = 0
        for msg in track:
            abs_time += msg.time
            if hasattr(msg, 'channel') and msg.channel == 9: 
                continue
            if msg.type in ['note_on', 'note_off']:
                events.append((abs_time, msg))

    events.sort(key=lambda x: x[0])

    ticks_per_beat = mid.ticks_per_beat
    active_notes = set()
    timeline_notes = []
    last_time = 0
    
    for abs_time, msg in events:
        delta_ticks = abs_time - last_time
        
        if delta_ticks > 0:
            duration_ms = int((delta_ticks * 500000) / (ticks_per_beat * 1000))
            if active_notes:
                highest_pitch = max(active_notes) # Monophonic melody extraction
                freq = int(440.0 * (2.0 ** ((highest_pitch - 69) / 12.0)))
                timeline_notes.append((freq, duration_ms))
            else:
                timeline_notes.append((0, duration_ms))
        
        if msg.type == 'note_on' and msg.velocity > 0:
            active_notes.add(msg.note)
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            active_notes.discard(msg.note)
            
        last_time = abs_time

    # Quantize note durations to 25ms steps for sharper timing precision
    TICK_MS = 25
    compressed = []
    
    for freq, dur in timeline_notes:
        if dur < 15: 
            continue
            
        idx = freq_to_idx(freq)
        ticks = max(1, min(255, int(round(dur / TICK_MS))))
        
        if compressed and compressed[-1][0] == idx:
            new_ticks = min(255, compressed[-1][1] + ticks)
            compressed[-1] = (idx, new_ticks)
        else:
            compressed.append((idx, ticks))

    total_original_notes = len(compressed)
    
    if len(compressed) > MAX_NOTES:
        compressed = compressed[:MAX_NOTES]
        compressed.append((0, 10)) # Clean end rest

    total_time_ms = sum(ticks * TICK_MS for _, ticks in compressed)
    minutes = int(total_time_ms // 60000)
    seconds = int((total_time_ms % 60000) // 1000)

    with open(output_h, "w") as f:
        f.write("#ifndef SONG_DATA_H\n#define SONG_DATA_H\n\n#include <avr/pgmspace.h>\n\n")
        f.write("struct CompressedNote {\n  uint8_t note_idx;\n  uint8_t ticks;\n};\n\n")
        f.write("const uint16_t note_freqs[] PROGMEM = {\n  " + ", ".join(map(str, NOTE_LOOKUP)) + "\n};\n\n")
        f.write("const CompressedNote full_midi_song[] PROGMEM = {\n")
        
        line = "  "
        for idx, ticks in compressed:
            entry = f"{{{idx},{ticks}}}, "
            if len(line) + len(entry) > 80:
                f.write(line + "\n")
                line = "  "
            line += entry
        f.write(line.rstrip(", ") + "\n};\n\n")
        f.write(f"const uint16_t full_midi_song_len = {len(compressed)};\n")
        f.write(f"const uint16_t BASE_TICK_MS = {TICK_MS};\n\n#endif\n")

    print("--------------------------------------------------")
    print(f"Original MIDI Notes: {total_original_notes}")
    if total_original_notes > MAX_NOTES:
        print(f"CUTOFF APPLIED: Truncated to {MAX_NOTES} notes.")
    else:
        print("FULL SONG FITS! No cutoff required.")
    print(f"Total Playtime: {minutes}m {seconds}s")
    print(f"Memory Footprint: {len(compressed) * 2} bytes")
    print("--------------------------------------------------")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        convert_midi_monophonic(sys.argv[1])
    else:
        print("Usage: python convert_midi.py your_song.mid")
