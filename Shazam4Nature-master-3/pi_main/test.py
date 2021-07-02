import json

with open('data_new.json') as file:

#with open('test.json') as file:
	data = file.read()
	obj = json.loads(data)
	for i in range(10):
		print(str(i) + ":" + str(obj[i]['classifications']))
#	print(obj[1]['classifications'])
