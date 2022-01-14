from itasca import p2pLinkClient
import subprocess
import numpy as np
from pyDemFoam import pyDemIcoFoam

solver = pyDemIcoFoam()

with p2pLinkClient() as pfc_link:
    pfc_link.connect("127.0.0.1")

    pfc_link.send_data(solver.nodes())
    pfc_link.send_data(solver.elements())
    pfc_link.send_data(solver.rho())
    pfc_link.send_data(solver.mu())

    oldn = solver.n()
    oldf = solver.f()
    r_factor = 1.0

    while True:
        print("waiting for run time")
        deltat = pfc_link.read_data()
        if deltat == 0.0:
            print ("solve finished")
            break
        print("got run time", deltat)
        newn = pfc_link.read_data()
        solver.n(oldn*(1-r_factor) + newn*r_factor)
        oldn = newn
        newf = pfc_link.read_data()
        solver.f(oldf*(1-r_factor) + newf*r_factor)
        oldf = newf
        print("got runtime and data")

        solver.set_dt(deltat)
        solver.solve(deltat)

        print("sending data to pfc")
        pfc_link.send_data(solver.p()*solver.rho())
        pfc_link.send_data(solver.gradp()*solver.rho())
        pfc_link.send_data(solver.U())
        print("send finished")
