import bpy


class OrderByX():


	def __init__(self):
		name = "CDPKey."
		allObjects = bpy.data.objects
		position = lambda sort: sort[1]
		objectNum = len(allObjects)
		sortList = [[0, 0] for i in range(objectNum)]

		for i in range(objectNum):
			sortList[i][0] = allObjects[i]
			sortList[i][1] = allObjects[i].location[0]

		sortList.sort(key = position)

		for i in range(objectNum):
			number = "00" + str(i)
			sortList[i][0].name = name + number[-3:]

OrderByX()

