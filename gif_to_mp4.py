import sys, imageio.v2 as imageio
from pathlib import Path

if len(sys.argv) < 3:
    print("Usage: python gif_to_mp4.py <in.gif> <out.mp4>")
    sys.exit(1)

ingif = Path(sys.argv[1])
outmp4 = Path(sys.argv[2])

reader = imageio.get_reader(str(ingif))
meta = reader.get_meta_data()
fps = int(meta.get('fps', 10)) or 10

writer = imageio.get_writer(str(outmp4), fps=fps, codec='libx264', pixelformat='yuv420p', quality=8)
for frame in reader:
    writer.append_data(frame)
writer.close()
print(outmp4)
