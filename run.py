#!/usr/bin/env python3
# Author: Benjamin T. James
import sys
import os
base_dir = "/srv/store/6.878"
prog = os.path.join(base_dir, "temp/6.878-Project/pipeline.py")
metadata = os.path.join(base_dir, "metadata.json")
dirname = os.path.join(base_dir, "bed")

def make_script(marker_list, feat_list=[], model_list=["svm", "mlp", "rf"]):
	sd_name = "_".join(marker_list)
	workdir = os.path.join(os.getcwd(), )
	marker_args = "-m " + ' -m '.join(marker_list)
	extra_args = ""
	if os.getenv('ARGS'):
		extra_args = os.getenv('ARGS')
	with open(sd_name + ".sh", 'w') as F:
		print("#!/usr/bin/env bash", file=F)
#		print("mkdir %s" % sd_name, file=F)
		print("cd %s" % sd_name, file=F)
		print("mkdir -p max && cd max", file=F)
		print("ln ../data.pickle .", file=F)
#		print("time python3 %s -j %s -d %s %s %s 2>&1 | tee output.txt" % (prog, metadata, dirname, marker_args, extra_args), file=F)
		print("time python3 %s -p data.pickle %s %s 2>&1 | tee output.txt" % (prog, marker_args, extra_args), file=F)
		print("", file=F)
		print("cd ..", file=F)

		print("mkdir min && cd min", file=F)
		print("time python3 %s -p ../max/data.pickle -b min 2>&1 %s | tee output.txt" % (prog, extra_args), file=F)
		print("", file=F)
		print("cd ..", file=F)
		print("", file=F)

		for model in model_list:
			dname = "%s_max" % model
			print("mkdir", dname, " && cd", dname, file=F)
			print("time python3 %s -p ../max/data.pickle -b max -r %s 2>&1 %s | tee output.txt" % (prog, model, extra_args), file=F)
			print("", file=F)
			print("cd ..", file=F)
			print("", file=F)
			dname = "%s_min" % model
			print("mkdir", dname, " && cd", dname, file=F)
			print("time python3 %s -p ../max/data.pickle -b min -r %s 2>&1 %s | tee output.txt" % (prog, model, extra_args), file=F)
			print("", file=F)
			print("cd ..", file=F)
			print("", file=F)
		for feat_num in feat_list:
			folder_name = "max%d" % feat_num
			print("", file=F)
			print("mkdir %s && cd %s" % (folder_name, folder_name), file=F)
			print("time python3 %s -p ../max/data.pickle -n %d 2>&1  %s| tee output.txt" % (prog, feat_num, extra_args), file=F)
			print("", file=F)
			print("cd ..", file=F)
			print("", file=F)

			folder_name = "min%d" % feat_num
			print("", file=F)
			print("mkdir %s && cd %s" % (folder_name, folder_name), file=F)
			print("time python3 %s -p ../max/data.pickle -b min -n %d 2>&1 %s | tee output.txt" % (prog, feat_num, extra_args), file=F)
			print("", file=F)
			print("cd ..", file=F)
			print("", file=F)
			for model in model_list:
				dname = "%s_max%d" % (model, feat_num)
				print("mkdir", dname, " && cd", dname, file=F)
				print("time python3 %s -p ../max/data.pickle -b max -n %d -r %s 2>&1 %s | tee output.txt" % (prog, feat_num, model, extra_args), file=F)
				print("", file=F)
				print("cd ..", file=F)
				print("", file=F)
				dname = "%s_min%d" % (model, feat_num)
				print("mkdir", dname, " && cd", dname, file=F)
				print("time python3 %s -p ../max/data.pickle -b min -n %d -r %s 2>&1 %s | tee output.txt" % (prog, feat_num, model, extra_args), file=F)
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
