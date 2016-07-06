from argparse import ArgumentParser
from pythreatgrid import threatgrid
from goatjockey import GoatJockey
from datetime import date, timedelta

def main(api_key, after, before):
	
	goat = GoatJockey(topx=1000000)

	options = {
		'api_key':api_key,
		'after': after,
		'before': before
	}
	domains = set()

	for page in threatgrid.domains(options):
		for domain in page[u'data'][u'items']:
			b = goat.match(domain[u'domain'])

			if not b[0]:
				domains.add(domain[u'domain'])

	for domain in domains:
		print(domain)

if __name__ == '__main__':
	parser = ArgumentParser('threatgrid', description='Download IOCs from threatgrid')
	parser.add_argument('api_key', type=str,
						help='API key for accessing ThreatGRID')
	parser.add_argument('-a', '--after', type=str,
						default=str(date.today()),
						help='Date to start on in YYYY-MM-DD format')
	parser.add_argument('-b', '--before', type=str,
						default=str(date.today() + timedelta(1)),
						help='Date to stop on in YYYY-MM-DD format')
	args = parser.parse_args()
	main(args.api_key, args.after, args.before)
