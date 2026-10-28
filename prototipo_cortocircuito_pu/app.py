import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Laboratorio de cortocircuito", page_icon="⚡", layout="wide")
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #f3f6fa; }
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
.hero { background: linear-gradient(120deg,#102a43,#176b87); padding: 1.5rem 1.8rem; border-radius: 18px; color: white; margin: .3rem 0 1.2rem 0; }
.hero h1 { color: white; margin: 0; font-size: 2rem; }
.hero p { color: #d5e8ef; margin: .45rem 0 0 0; }
.block-container { padding-top: 2rem; }
</style>
<div class="hero"><h1>Laboratorio de cortocircuito</h1><p>Modela la red, observa su diagrama unifilar y calcula la falla en valores por unidad.</p></div>
""", unsafe_allow_html=True)
st.caption("Análisis de falla trifásica balanceada · voltaje prefalla supuesto: 1∠0° pu")
st.write("Ingresa buses, generadores y líneas. Las impedancias de generador se capturan en pu sobre su base propia; las líneas aceptan pu u ohmios.")

c1,c2=st.columns(2)
with c1: sbase=st.number_input("Potencia base (MVA)",min_value=0.01,value=100.0,step=10.0)
with c2: st.number_input("Frecuencia (Hz, informativa)",min_value=1.0,value=60.0,step=1.0)
st.subheader("01 · Base y buses")
buses=st.data_editor(pd.DataFrame({"Bus":[1,2,3],"kV_base":[13.8,13.8,13.8]}),num_rows="dynamic",key="bus",use_container_width=True)
st.subheader("02 · Generadores")
gens=st.data_editor(pd.DataFrame({"Nombre":["G1"],"Bus":[1],"MVA_base":[100.0],"kV_base":[13.8],"R_pu":[0.0],"Xdp_pu":[0.2]}),num_rows="dynamic",key="gen",use_container_width=True)
st.caption("Xdp = reactancia subtransitoria X″d. R y Xdp se ingresan en pu sobre las bases MVA/kV propias del generador.")
st.subheader("03 · Líneas de transmisión")
lines=st.data_editor(pd.DataFrame({"Nombre":["L1","L2"],"Desde":[1,2],"Hasta":[2,3],"R":[0.0,0.0],"X":[0.1,0.1],"Unidad":["pu","pu"]}),num_rows="dynamic",key="line",use_container_width=True)
st.caption("Para líneas en ohmios, Zbase = kVbase²/MVAbase, usando el voltaje base del bus Desde.")
fault=st.selectbox("Bus de falla",options=list(buses["Bus"]) if len(buses) else [1])
zf=st.number_input("Impedancia de falla (pu; 0 = falla franca)",min_value=0.0,value=0.0,step=0.01)
st.subheader("Diagrama unifilar de la red")
st.caption("Vista automática de la topología capturada. El bus elegido para la falla aparece resaltado.")
def dot_escape(value): return str(value).replace('"','\\"')
try:
    bus_ids=[int(x) for x in buses["Bus"].dropna()]
    fault_int=int(fault)
    dot=['graph red {','rankdir=LR; bgcolor="transparent"; graph [pad="0.25", nodesep="0.55", ranksep="0.9", splines=true];','node [fontname="Arial", fontsize=11, style=filled, penwidth=1.7];','edge [fontname="Arial", fontsize=9, color="#58758a", penwidth=2];']
    for bus in bus_ids:
        fill="#d9534f" if bus==fault_int else "#dff3f5"
        color="#9e2824" if bus==fault_int else "#147d89"
        label=f"BUS {bus}\\n{float(buses.loc[buses.Bus==bus,'kV_base'].iloc[0]):g} kV"
        dot.append(f'B{bus} [label="{label}", shape=circle, width=1.05, height=1.05, fillcolor="{fill}", color="{color}", fontcolor="{("white" if bus==fault_int else "#17324d")}"];')
    for gi,(_,g) in enumerate(gens.dropna(subset=["Bus"]).iterrows()):
        bus=int(g.Bus)
        if bus in bus_ids:
            name=dot_escape(g.get("Nombre",f"G{gi+1}"))
            dot.append(f'G{gi} [label="⚡\\n{name}", shape=box, style="rounded,filled", fillcolor="#fff0cf", color="#d39b28", fontcolor="#59410d"];')
            dot.append(f'G{gi} -- B{bus} [style=dashed, color="#d39b28", label="X″d"];')
    for li,(_,line) in enumerate(lines.dropna(subset=["Desde","Hasta"]).iterrows()):
        a,b=int(line.Desde),int(line.Hasta)
        if a in bus_ids and b in bus_ids:
            nm=dot_escape(line.get("Nombre",f"L{li+1}"))
            dot.append(f'B{a} -- B{b} [label="{nm}  R+jX"];')
    dot.append('}')
    st.graphviz_chart("\n".join(dot), use_container_width=True)
except Exception as diagram_error:
    st.warning(f"Completa los datos de buses para mostrar el diagrama: {diagram_error}")

st.divider()

def num(row,key,default=0.):
    x=row.get(key,default)
    return float(x) if pd.notna(x) else default

if st.button("Calcular",type="primary"):
    try:
        ids=[int(x) for x in buses["Bus"]]
        if not ids or len(set(ids))!=len(ids): raise ValueError("Los buses deben tener números únicos.")
        ix={b:i for i,b in enumerate(ids)}; n=len(ids); Y=np.zeros((n,n),complex); gd=[]; ld=[]
        for _,g in gens.dropna(subset=["Bus"]).iterrows():
            bus=int(g.Bus)
            if bus not in ix: raise ValueError(f"Bus inexistente en generador {g.get('Nombre','')}.")
            sm=num(g,"MVA_base"); vg=num(g,"kV_base")
            if sm<=0 or vg<=0 or num(g,"Xdp_pu")<=0: raise ValueError("Las bases y Xdp de generador deben ser mayores que cero.")
            vsys=float(buses.loc[buses.Bus==bus,"kV_base"].iloc[0])
            z=complex(num(g,"R_pu"),num(g,"Xdp_pu"))*(sbase/sm)*(vg/vsys)**2
            if abs(z)==0: raise ValueError("Impedancia de generador no puede ser cero.")
            Y[ix[bus],ix[bus]]+=1/z; gd.append((str(g.get("Nombre","G")),bus,z))
        for _,l in lines.dropna(subset=["Desde","Hasta"]).iterrows():
            a,b=int(l.Desde),int(l.Hasta)
            if a not in ix or b not in ix: raise ValueError(f"Bus inexistente en línea {l.get('Nombre','')}.")
            z=complex(num(l,"R"),num(l,"X")); unit=str(l.get("Unidad","pu")).strip().lower()
            if unit in ["ohm","ohms","ohmios","ω"]:
                kv=float(buses.loc[buses.Bus==a,"kV_base"].iloc[0]); z/=kv**2/sbase
            elif unit!="pu": raise ValueError("Unidad de línea debe ser pu u ohmios.")
            if abs(z)==0: raise ValueError("Impedancia de línea no puede ser cero.")
            y=1/z;i,j=ix[a],ix[b];Y[i,i]+=y;Y[j,j]+=y;Y[i,j]-=y;Y[j,i]-=y;ld.append((str(l.get("Nombre","L")),a,b,z))
        k=ix[int(fault)]; Z=np.linalg.inv(Y); zth=Z[k,k]; ztotal=zth+zf
        if abs(ztotal)==0: raise ValueError("Impedancia equivalente de falla igual a cero.")
        kv=float(buses.loc[buses.Bus==int(fault),"kV_base"].iloc[0]); ibase=sbase/(np.sqrt(3)*kv); ifpu=1/ztotal
        # Voltajes de buses bajo falla franca; sirven para calcular aportes de cada fuente.
        rhs=np.zeros(n,complex)
        for _,b,z in gd: rhs[ix[b]]+=1/z
        if zf>0:
            Yfault=Y.copy(); Yfault[k,k]+=1/zf
            V=np.linalg.solve(Yfault,rhs)
        else:
            keep=[i for i in range(n) if i!=k]; V=np.zeros(n,complex)
            if keep: V[keep]=np.linalg.solve(Y[np.ix_(keep,keep)],rhs[keep])
        cont=[]
        for name,b,z in gd:
            ig=(1-V[ix[b]])/z
            cont.append({"Generador":name,"Bus":b,"Corriente (pu)":abs(ig),"Corriente (A)":abs(ig)*ibase})
        st.success("Cálculo completado.")
        a,b,c=st.columns(3);a.metric("Zth",f"{abs(zth):.4f} pu ∠ {np.angle(zth,deg=True):.2f}°");b.metric("Ifalla",f"{abs(ifpu):.4f} pu");c.metric("Ifalla",f"{abs(ifpu)*ibase:,.2f} A")
        st.write(f"Ibase en el bus {fault}: **{ibase:,.2f} A**. Ifalla compleja: **{ifpu.real:.4f} {ifpu.imag:+.4f}j pu**.")
        st.subheader("Aporte de generadores");st.dataframe(pd.DataFrame(cont),hide_index=True,use_container_width=True)
        st.subheader("Impedancias convertidas a base del sistema")
        rows=[{"Elemento":nm,"Tipo":"Generador","Conexión":str(b),"R (pu)":z.real,"X (pu)":z.imag} for nm,b,z in gd]+[{"Elemento":nm,"Tipo":"Línea","Conexión":f"{a}–{b}","R (pu)":z.real,"X (pu)":z.imag} for nm,a,b,z in ld]
        st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
        st.info("Modelo inicial educativo: no incluye flujo de carga prefalla, cargas, transformadores, secuencias ni fallas monofásicas/bifásicas.")
    except Exception as e: st.error(f"Revisa los datos: {e}")

with st.expander("Pasos del método por unidad"):
    st.markdown("1. Convertir impedancias a una base común.  2. Construir la matriz Ybus, incluyendo las fuentes detrás de X″d.  3. Obtener Zth visto desde el bus de falla.  4. Calcular If(pu) = 1/(Zth + Zf).  5. Convertir con Ibase = MVAbase/(√3·kVbase).")



