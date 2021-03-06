from num_solution import compute
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import animation
import argparse
import datetime
import math
import json
import numpy as np

def parseParameters():
    parser = argparse.ArgumentParser(description='.')
    parser.add_argument("-m", "--mode", help="what mode to run in; 3D, anim or 2D", action="store")
    parser.add_argument("-s", "--save", help="whether or not to save the figure", action="store_true")
    parser.add_argument("-S", "--settings", help="uses a supplied json-file as parameters. Will then ignore all other cmd parameters.", action="store")
    parser.add_argument("-t", "--time", help="give timespan and resolution on the form t0:t1:ts", action="store")
    parser.add_argument("-p", "--parameters", help="give parameters on the form m:w_0:xi_0:xi_dot_0", action="store")
    args = parser.parse_args()

    settings = {
        "mode" : "",
        "t1" : 0.0,
        "t2" : 10.0,
        "ts" : .01,
        "m" : 1.0,
        "omega_0" : math.pi,
        "xi_0" : 10.0,
        "xi_dot_0" : 0,
        "save" : False
    }

    if(args.settings != None):
        with open(str(args.settings)) as settings_file:
            settings = json.loads(settings_file.read())
            settings["computePos"] = settings["mode"] == "3d" or settings["mode"] == "anim"
    else:

        settings["mode"] = str(args.mode).lower()
        settings["computePos"] = settings["mode"] == "3d" or settings["mode"] == "anim"
        settings["save"]  = args.save

        if(args.time != None):
            time_str = str(args.time).split(":")
            settings["t1"] = float(time_str[0])
            settings["t2"] = float(time_str[1])
            settings["ts"] = float(time_str[2]) if settings["mode"] != "anim" else (1/30)

        if(args.parameters != None):
            parameter_str = str(args.parameters).split(":")
            settings["m"] = float(parameter_str[0])
            settings["omega_0"] = float(parameter_str[1])
            settings["xi_0"] = float(parameter_str[2])
            settings["xi_dot_0"] = float(parameter_str[3])

    print("Running with the following parameters:")
    print("Mass:".ljust(12).rjust(16), settings["m"])
    print("Omega:".ljust(12).rjust(16), settings["omega_0"])
    print("Position:".ljust(12).rjust(16), settings["xi_0"])
    print("Velocity:".ljust(12).rjust(16), settings["xi_dot_0"])
    print("Timespan:".ljust(12).rjust(16), str(settings["t2"])+" -> "+str(settings["t2"]))
    print("Timestep:".ljust(12).rjust(16), settings["ts"])

    return settings

def main():
    settings = parseParameters()

    t, out = compute(
        T=(settings["t1"], settings["t2"]), 
        substep=settings["ts"], 
        xi_0=settings["xi_0"], 
        xi_vel_0=settings["xi_dot_0"], 
        m_0=settings["m"], 
        omega_0=settings["omega_0"], 
        computePos=settings["computePos"]
    )
    ani = None
    if(settings["mode"] == "2d"):
       plt.plot(t, out)
    elif(settings["mode"] == "3d"):
        fig = plt.figure()
        ax = fig.add_subplot(111,projection='3d')
        X = list([p[0] for p in out])
        Y = list([p[1] for p in out])
        Z = list([p[2] for p in out])
        ax.plot(X,Y,Z)
    elif(settings["mode"] == "anim"):
        
        fig = plt.figure()
        ax = Axes3D(fig)
        plot = ax.scatter([out[0][0]], [out[0][1]], [out[0][2]], alpha=0.8)
        x = [out[0][0]]
        y = [out[0][1]]
        z = [out[0][2]]

        soa = np.array([
        [0, 0, 0, 10*math.cos(w_0 * t[0]), 10*math.sin(w_0 * t[0]), 0], 
        [0, 0, 0, 10*math.sin(w_0 * t[0]), 10*math.cos(w_0 * t[0]), 0], 
        [0, 0, 0, 0, 0, 10] 
        ])

        X, Y, Z, U, V, W = zip(*soa)
        global unitXi
        unitXi = ax.quiver(X, Y, Z, U, V, W, color="black")

        def animate(iteration):
            i = iteration
            
            # update quiver
            soa = np.array([
            [0, 0, 0, 10*math.cos(w_0 * t[i]), 10*math.sin(w_0 * t[i]), 0], 
            [0, 0, 0, 10*math.cos(w_0 * t[i]+math.pi/2), 10*math.sin(w_0 * t[i]+math.pi/2), 0], 
            [0, 0, 0, 0, 0, 35] 
            ])

            X, Y, Z, U, V, W = zip(*soa)
            global unitXi
            unitXi.remove()
            unitXi = ax.quiver(X, Y, Z, U, V, W, color="black")

            # Update point
            x.clear()
            y.clear()
            z.clear()
            x.append(out[i][0])
            y.append(out[i][1])
            z.append(out[i][2])
            plot._offsets3d = (x,y,z)

            return plot,

        sorted_x = sorted([out[i][0] for i in range(len(out))])
        sorted_y = sorted([out[i][1] for i in range(len(out))])
        sorted_z = sorted([out[i][2] for i in range(len(out))])


        x_min = float(sorted_x[0])
        y_min = float(sorted_y[0])
        z_min = float(sorted_z[0])
        
        x_max = float(sorted_x[-1])
        y_max = float(sorted_y[-1])
        z_max = float(sorted_z[-1])
        
        print(z_min, z_max)

        ax.set_xlim3d([-x_max, x_max])
        ax.set_xlabel('X')

        ax.set_ylim3d([-x_max, x_max])
        ax.set_ylabel('Y')

        ax.set_zlim3d([z_min, z_max])
        ax.set_zlabel('Z')

        ani = animation.FuncAnimation(fig, animate, len(out), interval=(ts*1000), blit=False, repeat=True)

    else:
        raise Exception(f"Not supported mode: {mode_str}")


    if(save):
        extention = "png" if mode_str == "3d" or mode_str == "2d" else "gif"
        time_str = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        file_name = f"figures/fig_{time_str}.{extention}"
        if(mode_str == "3d" or mode_str == "2d"):
            plt.savefig(file_name)
        elif(ani != None):
            print(int(1/ts))
            ani.save(file_name)
    else:
        plt.show()


if(__name__ == "__main__"):
    main()