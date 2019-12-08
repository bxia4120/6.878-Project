#!/usr/bin/env python3
# Author: Benjamin T. James
import sys
import os
base_dir = "/srv/store/6.878"
prog = os.path.join(base_dir, "temp/6.878-Project/pipeline.py")
metadata = os.path.join(base_dir, "metadata.json")
dirname = os.path.join(base_dir, "bed")

def make_script(marker_list, feat_list=[]):
	sd_name = "_".join(marker_list)
	workdir = os.path.join(os.getcwd(), )
	marker_args = "-m " + ' -m '.join(marker_list)
	with open(sd_name + ".sh", 'w') as F:
		print("#!/usr/bin/env bash", file=F)
		print("mkdir %s" % sd_name, file=F)
		print("cd %s" % sd_name, file=F)
		print("mkdir -p max && cd max", file=F)
		print("time python3 %s -j %s -d %s %s 2>&1 | tee output.txt" % (prog, metadata, dirname, marker_args), file=F)
		print("", file=F)
		print("cd ..", file=F)
		print("ln max/data.pickle .", file=F)

		print("", file=F)
		print("mkdir c_max && cd c_max", file=F)
		print("time python3 %s -p ../max/data.pickle -b max -t class 2>&1 | tee output.txt" % (prog,), file=F)
		print("", file=F)
		print("cd ..", file=F)
		print("", file=F)

		print("", file=F)
		print("mkdir m_max && cd m_max", file=F)
		print("time python3 %s -p ../max/data.pickle -b max -t multi 2>&1 | tee output.txt" % (prog,), file=F)
		print("", file=F)
		print("cd ..", file=F)
		print("", file=F)

		print("", file=F)
		print("mkdir min && cd min", file=F)
		print("time python3 %s -p ../max/data.pickle -b min 2>&1 | tee output.txt" % (prog,), file=F)
		print("", file=F)
		print("cd ..", file=F)
		print("", file=F)

		print("", file=F)
		print("mkdir c_min && cd c_min", file=F)
		print("time python3 %s -p ../max/data.pickle -b min -t class 2>&1 | tee output.txt" % (prog,), file=F)
		print("", file=F)
		print("cd ..", file=F)
		print("", file=F)

		print("", file=F)
		print("mkdir m_min && cd m_min", file=F)
		print("time python3 %s -p ../max/data.pickle -b min -t multi 2>&1 | tee output.txt" % (prog,), file=F)
		print("", file=F)
		print("cd ..", file=F)
		print("", file=F)
		for feat_num in feat_list:
			folder_name = "max%d" % feat_num
			print("", file=F)
			print("mkdir %s && cd %s" % (folder_name, folder_name), file=F)
			print("time python3 %s -p ../max/data.pickle -n %d 2>&1 | tee output.txt" % (prog, feat_num), file=F)
			print("", file=F)
			print("cd ..", file=F)
			print("", file=F)

			folder_name = "min%d" % feat_num
			print("", file=F)
			print("mkdir %s && cd %s" % (folder_name, folder_name), file=F)
			print("time python3 %s -p ../max/data.pickle -b min -n %d 2>&1 | tee output.txt" % (prog, feat_num), file=F)
			print("", file=F)
			print("cd ..", file=F)
			print("", file=F)

			folder_name = "c_max%d" % feat_num
			print("", file=F)
			print("mkdir %s && cd %s" % (folder_name, folder_name), file=F)
			print("time python3 %s -p ../max/data.pickle -n %d -t class 2>&1 | tee output.txt" % (prog, feat_num), file=F)
			print("", file=F)
			print("cd ..", file=F)
			print("", file=F)

			folder_name = "c_min%d" % feat_num
			print("", file=F)
			print("mkdir %s && cd %s" % (folder_name, folder_name), file=F)
			print("time python3 %s -p ../max/data.pickle -b min -n %d -t class 2>&1 | tee output.txt" % (prog, feat_num), file=F)
			print("", file=F)
			print("cd ..", file=F)
			print("", file=F)

			folder_name = "m_max%d" % feat_num
			print("", file=F)
			print("mkdir %s && cd %s" % (folder_name, folder_name), file=F)
			print("time python3 %s -p ../max/data.pickle -n %d -t multi 2>&1 | tee output.txt" % (prog, feat_num), file=F)
			print("", file=F)
			print("cd ..", file=F)
			print("", file=F)

			folder_name = "m_min%d" % feat_num
			print("", file=F)
			print("mkdir %s && cd %s" % (folder_name, folder_name), file=F)
			print("time python3 %s -p ../max/data.pickle -b min -n %d -t multi 2>&1 | tee output.txt" % (prog, feat_num), file=F)
			print("", file=F)
			print("cd ..", file=F)
			print("", file=F)

	os.system("chmod u+x %s.sh" % sd_name)
if __name__ == "__main__":
	if len(sys.argv) == 0:
		print("Usage: %s " % sys.argv[0])
		sys.exit(1)
	nfeat_list = list(map(int, filter(lambda x: x.isnumeric(), sys.argv[1:])))
	m_list = list(filter(lambda x: not x.isnumeric(), sys.argv[1:]))
	for marker in m_list:
		make_script([marker], feat_list=nfeat_list)
