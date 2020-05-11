from random import choice
from base64 import b64encode
from app.app import make_app
from app.models import PPE

app, db, migrate, bootstrap, login = make_app(__name__)

def read_image(name):
	with open(name, 'rb') as f:
		data = f.read()
		return b"data:image/jpeg;base64," + b64encode(data)

IMAGES = list(map(read_image, ['mask_1.jpeg', 'mask_2.jpeg','mask_3.jpg']))

with app.app_context():
	for name in ['N90', 'N95', 'N97', 'N99', 'Surgical']:
		for size in ['Small', 'Medium', 'Large']: # I'm pretty sure this isn't how masks are sized
			ppe = PPE(
				sku="{}-{}".format(name.upper(), size[0]),
				desc="A {} mask in the {} size. Suitable for various uses. Not flame resistant. Does not contain platnum. Produced by the Sheinhardt Wig Company.".format(name, size) ,
				img = choice(IMAGES),
			)
			db.session.add(ppe)
	db.session.commit()
	