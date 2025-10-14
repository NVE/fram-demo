from multiprocessing import Process

from framdemo.demo_1_download_dataset import demo_1_download_dataset
from framdemo.demo_2_populate_model import demo_2_populate_model
from framdemo.demo_3_solve_model import demo_3_solve_model
from framdemo.demo_4_modified_solve import demo_4_modified_solve
from framdemo.demo_5_detailed_solve import demo_5_detailed_solve
from framdemo.demo_6_nordic_solve import demo_6_nordic_solve
from framdemo.demo_7_get_data import demo_7_get_data
from framdemo.demo_8_run_dashboard import demo_8_run_dashboard

if __name__ == "__main__":
    demo_1_download_dataset()
    demo_2_populate_model()
    demo_3_solve_model(num_cpu_cores=8)

    # run demo 4, 5 and 6 in parallel
    procs: list[Process] = [
        Process(target=demo_4_modified_solve, args=(1,)),  # arg is num_cpu_cores
        Process(target=demo_5_detailed_solve, args=(6, )), # arg is num_cpu_cores
        Process(target=demo_6_nordic_solve, args=(1, )),   # arg is num_cpu_cores
    ]
    for p in procs:
        p.start()
    for p in procs:
        p.join()

    # these will not execute until demo 4, 5 and 6
    # are done due to the join calls above
    demo_7_get_data()
    demo_8_run_dashboard()
