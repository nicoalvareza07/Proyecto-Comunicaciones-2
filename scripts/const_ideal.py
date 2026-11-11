import sys, math, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
out=sys.argv[1]
Q=np.array([1+0j,0+1j,0-1j,-1+0j]); X=np.array([-3-3j,-3-1j,-3+3j,-3+1j,-1-3j,-1-1j,-1+3j,-1+1j,3-3j,3-1j,3+3j,3+1j,1-3j,1-1j,1+3j,1+1j])/math.sqrt(10)
plt.rcParams.update({"font.size":10,"axes.grid":True,"grid.color":"#e4e3df","figure.dpi":150,"savefig.bbox":"tight"})
fig,ax=plt.subplots(1,2,figsize=(11,5.2))
for A,T,col,name,k in [(ax[0],Q,"#2a78d6","QPSK (M=4, k=2)",2),(ax[1],X,"#eb6834","16QAM (M=16, k=4, Gray)",4)]:
    A.axhline(0,color="#52514e",lw=.8);A.axvline(0,color="#52514e",lw=.8)
    A.scatter(T.real,T.imag,s=90,color=col,edgecolors="white",linewidths=1.5,zorder=3)
    for i,z in enumerate(T): A.annotate(format(i,f"0{k}b"),(z.real,z.imag),xytext=(0,10),textcoords="offset points",ha="center",fontsize=9,color="#0b0b0b")
    A.set_xlim(-1.35,1.35);A.set_ylim(-1.35,1.35);A.set_aspect("equal")
    A.set_xlabel("En fase I");A.set_ylabel("Cuadratura Q");A.set_title(name,fontweight="bold")
dq=abs(Q[0]-Q[1]); dx=2/math.sqrt(10)
ax[0].annotate("",xy=(0,1),xytext=(1,0),arrowprops=dict(arrowstyle="<->",color="#52514e"))
ax[0].text(0.58,0.58,f"d_min = √2 ≈ {dq:.2f}",fontsize=9,color="#52514e")
ax[1].annotate("",xy=(X[13].real,X[13].imag-0.12),xytext=(X[9].real,X[9].imag-0.12),arrowprops=dict(arrowstyle="<->",color="#52514e"))
ax[1].text(0.30,-0.62,f"d_min = 2/√10 ≈ {dx:.2f}",fontsize=9,color="#52514e")
fig.suptitle("Constelaciones ideales de referencia con energía promedio Es = 1 (etiqueta = bits del símbolo)",fontweight="bold")
fig.savefig(out)
