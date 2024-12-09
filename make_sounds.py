import wave
import struct
import math
import numpy as np
import random

def create_sound(filename, frequency, duration, volume=0.5, sample_rate=44100):
    # Generate samples
    samples = []
    num_samples = int(duration * sample_rate)
    
    for i in range(num_samples):
        t = float(i) / sample_rate
        sample = volume * math.sin(2.0 * math.pi * frequency * t)
        # Add quick fade out
        if i > num_samples * 0.7:
            sample *= (1.0 - ((i - num_samples * 0.7) / (num_samples * 0.3)))
        samples.append(sample)
    
    # Pack samples into wave file
    with wave.open(filename, 'w') as wav_file:
        # Set parameters
        nchannels = 1
        sampwidth = 2
        framerate = sample_rate
        nframes = len(samples)
        comptype = "NONE"
        compname = "not compressed"
        
        wav_file.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))
        
        # Write samples
        for sample in samples:
            # Convert to 16-bit integer
            packed_value = struct.pack('h', int(max(-32767, min(32767, sample * 32767.0))))
            wav_file.writeframes(packed_value)

def create_oof_sound(filename, sample_rate=44100):
    duration = 0.3
    samples = []
    num_samples = int(duration * sample_rate)
    
    # Create a more complex "oof" sound with multiple frequencies
    for i in range(num_samples):
        t = float(i) / sample_rate
        
        # Base frequency that drops (like "oo" sound)
        freq1 = 200 - (100 * t / duration)
        # Higher frequency for the "f" sound
        freq2 = 800 * math.exp(-5 * t)
        
        # Combine frequencies with different amplitudes
        sample = 0.7 * math.sin(2.0 * math.pi * freq1 * t)
        sample += 0.3 * math.sin(2.0 * math.pi * freq2 * t)
        
        # Add some noise for the "f" sound
        if t > 0.2:
            sample += 0.2 * (2 * random.random() - 1)
        
        # Envelope
        if i < sample_rate * 0.1:  # Attack
            sample *= (i / (sample_rate * 0.1))
        elif i > sample_rate * 0.2:  # Release
            sample *= (1.0 - ((i - sample_rate * 0.2) / (sample_rate * 0.1)))
            
        samples.append(sample)
    
    # Pack samples into wave file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setparams((1, 2, sample_rate, len(samples), "NONE", "not compressed"))
        for sample in samples:
            packed_value = struct.pack('h', int(max(-32767, min(32767, sample * 32767.0))))
            wav_file.writeframes(packed_value)

def create_ouch_sound():
    # Create a short "ouch" sound
    sample_rate = 44100
    duration = 0.4  # Longer duration
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create a more pronounced "ou" sound
    freq_start = 600  # Higher start frequency
    freq_end = 300   # Higher end frequency
    freq = np.linspace(freq_start, freq_end, len(t))
    ou_sound = np.sin(2 * np.pi * freq * t) * 0.8  # Louder amplitude
    
    # Add some vibrato for more expression
    vibrato = np.sin(2 * np.pi * 12 * t) * 20
    ou_sound = np.sin(2 * np.pi * (freq + vibrato) * t) * 0.8
    
    # Create a stronger "ch" sound
    ch_duration = 0.15
    ch_samples = int(sample_rate * ch_duration)
    ch_sound = np.random.normal(0, 0.5, ch_samples)  # More noise
    ch_sound = np.pad(ch_sound, (len(t) - len(ch_sound), 0))
    
    # Combine sounds
    combined = ou_sound + ch_sound
    
    # Apply smoother envelope
    envelope = np.exp(-2 * t)  # Slower decay
    sound = combined * envelope
    
    # Amplify the final sound
    return sound * 1.5  # Increased overall volume

def make_sword_hit_sound():
    duration = 0.1  # seconds
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Higher amplitude for louder sound
    hit = np.sin(2 * np.pi * 440 * t) * 0.8
    hit *= np.exp(-7 * t)  # Sharp decay
    
    return hit

def make_bow_hit_sound():
    duration = 0.15
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Higher amplitude for louder sound
    hit = np.sin(2 * np.pi * 550 * t) * 0.8
    hit *= np.exp(-5 * t)
    
    return hit

def make_spear_hit_sound():
    duration = 0.2
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Higher amplitude for louder sound
    hit = np.sin(2 * np.pi * 330 * t) * 0.8
    hit *= np.exp(-4 * t)
    
    return hit

def make_ouch_sound():
    duration = 0.4  # Longer duration
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Higher frequency for more pronounced sound
    freq = 400 + np.sin(2 * np.pi * 5 * t) * 50  # Add vibrato
    
    # Higher amplitude for louder sound
    ouch = np.sin(2 * np.pi * freq * t) * 0.9
    
    # Envelope for natural sound
    envelope = np.exp(-3 * t)
    ouch *= envelope
    
    return ouch

# Create sword swing sound (higher pitch, shorter)
create_sound('sounds/sword_swing.wav', 440, 0.15)

# Create sword hit sound (lower pitch, sharp)
create_sound('sounds/sword_hit.wav', 220, 0.1)

# Create jump sound (rising pitch)
samples = []
sample_rate = 44100
duration = 0.2
for i in range(int(duration * sample_rate)):
    t = float(i) / sample_rate
    frequency = 300 + (1000 * t / duration)
    sample = 0.5 * math.sin(2.0 * math.pi * frequency * t)
    if i > sample_rate * duration * 0.7:
        sample *= (1.0 - ((i - sample_rate * duration * 0.7) / (sample_rate * duration * 0.3)))
    samples.append(sample)

with wave.open('sounds/jump.wav', 'w') as wav_file:
    wav_file.setparams((1, 2, sample_rate, len(samples), "NONE", "not compressed"))
    for sample in samples:
        packed_value = struct.pack('h', int(max(-32767, min(32767, sample * 32767.0))))
        wav_file.writeframes(packed_value)

# Create button click sound (short, sharp)
create_sound('sounds/button_click.wav', 880, 0.05)

# Create a more painful hit sound
sample_rate = 44100
duration = 0.3
samples = []

for i in range(int(duration * sample_rate)):
    t = float(i) / sample_rate
    # Base painful sound (mix of frequencies)
    sample = 0.5 * math.sin(2.0 * math.pi * 180 * t)  # Low painful groan
    sample += 0.3 * math.sin(2.0 * math.pi * 350 * t)  # Mid painful tone
    sample += 0.2 * math.sin(2.0 * math.pi * 600 * t)  # High painful accent
    
    # Add vibrato for more pain effect
    vibrato = math.sin(2.0 * math.pi * 12 * t)
    sample *= (1.0 + 0.2 * vibrato)
    
    # Add envelope
    if i < sample_rate * 0.05:  # Sharp attack
        sample *= (i / (sample_rate * 0.05))
    elif i > sample_rate * 0.2:  # Longer release
        sample *= (1.0 - ((i - sample_rate * 0.2) / (sample_rate * 0.1)))
    
    samples.append(sample)

with wave.open('sounds/painful_hit.wav', 'w') as wav_file:
    wav_file.setparams((1, 2, sample_rate, len(samples), "NONE", "not compressed"))
    for sample in samples:
        packed_value = struct.pack('h', int(max(-32767, min(32767, sample * 32767.0))))
        wav_file.writeframes(packed_value)

# Create a more realistic oof sound
create_oof_sound('sounds/oof.wav')

# Create a better Roblox-style "oof" sound
sample_rate = 44100
duration = 0.1  # Even shorter, more like Roblox
samples = []

for i in range(int(duration * sample_rate)):
    t = float(i) / sample_rate
    # Classic Roblox "oof" is more like "uuf"
    frequency = 350 - (500 * t / duration)  # Different frequency range
    
    # Add a second frequency for the "oo" part
    freq2 = 200 - (300 * t / duration)
    
    # Combine frequencies
    sample = 0.7 * math.sin(2.0 * math.pi * frequency * t)
    sample += 0.3 * math.sin(2.0 * math.pi * freq2 * t)
    
    # Sharper envelope for that classic Roblox feel
    if i < sample_rate * 0.02:  # Very quick attack
        sample *= (i / (sample_rate * 0.02))
    elif i > sample_rate * 0.07:  # Quick decay
        sample *= (1.0 - ((i - sample_rate * 0.07) / (sample_rate * 0.03)))
    
    samples.append(sample)

with wave.open('sounds/roblox_oof.wav', 'w') as wav_file:
    wav_file.setparams((1, 2, sample_rate, len(samples), "NONE", "not compressed"))
    for sample in samples:
        packed_value = struct.pack('h', int(max(-32767, min(32767, sample * 32767.0))))
        wav_file.writeframes(packed_value)

# Create ouch sound
sound = create_ouch_sound()
with wave.open('sounds/ouch.wav', 'w') as wav_file:
    wav_file.setparams((1, 2, 44100, len(sound), "NONE", "not compressed"))
    for sample in sound:
        packed_value = struct.pack('h', int(max(-32767, min(32767, sample * 32767.0))))
        wav_file.writeframes(packed_value)

# Create sword hit sound
sound = make_sword_hit_sound()
with wave.open('sounds/sword_hit.wav', 'w') as wav_file:
    wav_file.setparams((1, 2, 44100, len(sound), "NONE", "not compressed"))
    for sample in sound:
        packed_value = struct.pack('h', int(max(-32767, min(32767, sample * 32767.0))))
        wav_file.writeframes(packed_value)

# Create bow hit sound
sound = make_bow_hit_sound()
with wave.open('sounds/bow_hit.wav', 'w') as wav_file:
    wav_file.setparams((1, 2, 44100, len(sound), "NONE", "not compressed"))
    for sample in sound:
        packed_value = struct.pack('h', int(max(-32767, min(32767, sample * 32767.0))))
        wav_file.writeframes(packed_value)

# Create spear hit sound
sound = make_spear_hit_sound()
with wave.open('sounds/spear_hit.wav', 'w') as wav_file:
    wav_file.setparams((1, 2, 44100, len(sound), "NONE", "not compressed"))
    for sample in sound:
        packed_value = struct.pack('h', int(max(-32767, min(32767, sample * 32767.0))))
        wav_file.writeframes(packed_value)

# Create ouch sound
sound = make_ouch_sound()
with wave.open('sounds/ouch.wav', 'w') as wav_file:
    wav_file.setparams((1, 2, 44100, len(sound), "NONE", "not compressed"))
    for sample in sound:
        packed_value = struct.pack('h', int(max(-32767, min(32767, sample * 32767.0))))
        wav_file.writeframes(packed_value)
