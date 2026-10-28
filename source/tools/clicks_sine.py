import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
for f in sys.argv[1:]:
    sr,x=wavfile.read(f); x=x.astype(np.float64)/32768
    h=sosfilt(butter(8,2500,"high",fs=sr,output="sos"),x)   # the test tones are all below 600 Hz
    win=int(0.002*sr); n=len(h)//win; e=np.abs(h[:n*win].reshape(n,win)).max(1)
    lvl=np.abs(x).max()
    bad=np.where(e>0.004)[0]
    print(f"{f}: loudest click {e.max()*1000:.2f}/1000 of full scale ({20*np.log10(e.max()/lvl+1e-12):.0f} dB below the signal) · slices over the limit: {len(bad)}"+("" if not len(bad) else "  at "+", ".join(f"{i*win/sr:.2f}s" for i in bad[:10])))
