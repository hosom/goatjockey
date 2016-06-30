from argparse import ArgumentParser

from goatjockey import GoatJockey
from OTXv2 import OTXv2

def main(api_key, start_date):

	goat = GoatJockey(topx=1000000)
	otx = OTXv2(api_key)

	interesting_iocs = set()

	for pulse in otx.getsince_iter(start_date):
		for indicator in pulse['indicators']:
			if indicator['type'] in collected_types:
				b = goat.match(indicator['indicator'])

				if not b[0]: 
					interesting_iocs.add(indicator['indicator'])

	for ioc in interesting_iocs:
		print(ioc)

if __name__ == '__main__':
	parser = ArgumentParser('otx', description='Download OTX and verify it against GoatJockey')
	parser.add_argument('api_key', type=str,
						help='API key for accessing OTX')
	parser.add_argument('start_date', type=str,
						help='Date to start intel pull on.')
	args = parser.parse_args()
	main(args.api_key, args.start_date)