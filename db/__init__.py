import oursql

conn = oursql.connect(db='eve', user='eve', passwd='eve', autoreconnect=True)
