import sounddevice as sd

apis = [a['name'] for a in sd.query_hostapis()]
print("APIs:", apis)
for i, d in enumerate(sd.query_devices()):
    if d['max_input_channels'] > 0:
        api_name = apis[d['hostapi']]
        print(f"[{i}] ({api_name}) {d['name']} (in channels: {d['max_input_channels']}, default SR: {d['default_samplerate']})")
