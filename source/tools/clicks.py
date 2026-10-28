"""Find clicks/pops: a click is a sudden jump in the waveform, which shows up as a burst of very high
frequencies that the crowd recordings themselves don't have (they're MP3s with nothing much above ~8 kHz)."""
import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
for f in sys.argv[1:]:
    sr,x=wavfile.read(f); x=x.astype(np.float64)/32768
    h=sosfilt(butter(6,8500,"high",fs=sr,output="sos"),x)
    win=int(0.002*sr); n=len(h)//win; e=np.sqrt((h[:n*win].reshape(n,win)**2).mean(1))+1e-7
    # compare each 2 ms slice with the typical level around it (median of the surrounding 0.2 s)
    k=50; med=np.array([np.median(e[max(0,i-k):i+k]) for i in range(n)])
    ratio=e/med; hits=np.where(ratio>8)[0]
    # also the plain sample-to-sample jump, relative to the local signal size
    d=np.abs(np.diff(x)); loud=np.sqrt(np.convolve(x**2,np.ones(441)/441,"same"))[1:]+1e-4
    jumps=(d/loud)
    print(f"{f}: high-freq bursts >8x: {len(hits)}  worst {ratio.max():.1f}x at {np.argmax(ratio)*win/sr:.2f}s  | worst sample jump {jumps.max():.1f}x local RMS at {np.argmax(jumps)/sr:.2f}s")
    if len(hits): print("   at", ", ".join(f"{i*win/sr:.2f}s" for i in hits[:12]))
