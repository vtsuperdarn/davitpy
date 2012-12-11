import pymongo as pm

def test():
	
	conn = pm.MongoClient('localhost')
	
	db = conn.testDb
	
	coll = db.radData
	
	beams = db.beams
	
	beam = {'bmnum': 15,
					'ptab': [1,2,3,4,5]}
	
	pid = beams.insert(beam)
	
	pid