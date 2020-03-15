import bpy


class OrderByX():


	def __init__(self):
		"""
		This will search all of the objects in the room, and apply a suffix to objects with a specified name in ascending order, E.G name.000, name.001.
		This order is determined by their x coordinate (lower number = lower suffix), so things will need to be ordered along the x axis.

		This could also be reworked quite easily to change the starting name of the object, essentially turning this code into a renaming script:
		E.G find all objects with "button" at the start of their name, and change them to "key"
		"""
		name = "CDPKey." # The name of the objects you want to find.
		# # There should be nothing before the name, but the suffix doesn't matter

		nameLen = len(name) # Length of the name, will be used to check if an object should have its name modified.
		allObjects = bpy.data.objects
		position = lambda sort: sort[1] # In the 2D array, return the second entry, which is the position in the X axis.
			# Also, my IDE telling me "do not assign a lambda expression just use a def lol" is going to make me explode with anger heck you PEP 8 I want readability
		objectNum = len(allObjects)
		sortList = [] # Build the list to be the max amount of objects. This will always leave unused values, but will be easier on the CPU.

		j = 0
		for i in range(objectNum):
			doesObjectNameMatch = allObjects[i].name[:nameLen] == name # This will only impact objects that start with the name variable, above.
			if(doesObjectNameMatch): # If this is one of the key objects designed to be ordered...
				sortList.append([])
				sortList[j].append(allObjects[i])
				sortList[j].append(allObjects[i].location[0])
				j += 1


		# Sort into order, from -x to +x (Based on object origin)
		sortList.sort(key = position) # Sort based on the X. Higher (positive) X will return a higher position.
		toSortNumber = len(sortList)

		# Rename all of the objects based on the sorted list.
		for i in range(toSortNumber):
			number = "00" + str(i)
			sortList[i][0].name = name + number[-3:]


		# Align all object origins along the Y axis.
		targetYPosition = 2.8 / 100

		for i in range(toSortNumber):
			obj = sortList[i][0]
			objectPosition = obj.location
			distanceFromY = targetYPosition - objectPosition[1]

			obj.location = ([objectPosition[0], targetYPosition, objectPosition[2]]) # Move the whole object (origin) to the desired spot.











OrderByX()

