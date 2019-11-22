import json
import os

metadata = json.load(open('metadata.json'))

valid_samples = set()

healthy_synonyms = set(['none', 'normal', 'healthy', 'presumed_normal'])

for sample_id, sample_info in metadata['samples'].items():
	if sample_info.get('disease', 'absent').lower() in healthy_synonyms:
		if any([i.isdigit() for i in str(sample_info.get('donor_age', 'NA'))]):
			valid_samples.add(sample_id)
			# NEED TO DO AGE PARSING
			'''if '-' in str(sample_info['donor_age']):
				age_range = sample_info['donor_age'].split('-')'''

if not os.path.exists('./data'):
	os.system('mkdir data')

for sample_id in valid_samples:
	if sample_id + '_H3K27ac' in metadata['datasets']:
		for sample_data in metadata['datasets'][sample_id + '_H3K27ac']['browser']['peak_calls']:
			if not os.path.exists('./data/' + sample_data['big_data_url'].split('/')[-1]):
				os.system('wget ' + sample_data['big_data_url'] + ' --no-check-certificate -P ./data')