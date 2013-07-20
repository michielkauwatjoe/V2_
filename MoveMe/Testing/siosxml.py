from MoveMe.Sios import device

def main():
	device = device.device()
	dev = device.from_uri('http://isp.v2.nl/~simon/data/sios.xml')
	print dev

if __name__ == "__main__":
	main()
