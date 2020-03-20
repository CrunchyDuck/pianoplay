import bpy
import copy

class DupeKeyMaterials():

	def __init__(self):
		keyArray = self.getKeyObjectList()
		keyHeight = self.getKeyElevations(keyArray) # The point half way between black and white keys on the Z axis.
		allMaterials = copy.copy(bpy.data.materials)
		keyMatBlack = allMaterials["BlackKey"]
		keyMatWhite = allMaterials["WhiteKey"]
		whiteKeyList, blackKeyList = self.sortBlackAndWhite(keyArray, keyHeight)

		mat = allMaterials.new(name = "BlackKey2")





	def getKeyObjectList(self):
		"""
		Gets a list of all key objects.
		::return:: 2D array containing object and object y position
		"""
		name = "CDPKey."  # The name of the objects you want to find.
		# There should be nothing before the name, but the suffix doesn't matter

		nameLen = len(name)  # Length of the name, will be used to check if an object should have its name modified.
		allObjects = bpy.data.objects # Get a list of all objects in the blend file.
		objectNum = len(allObjects)
		objectArray = []  # Build the list to be the max amount of objects. This will always leave unused values, but will be easier on the CPU.

		j = 0
		for i in range(objectNum):
			doesObjectNameMatch = allObjects[i].name[:nameLen] == name  # This will only impact objects that start with the name variable, above.
			if (doesObjectNameMatch):  # If this is one of the key objects designed to be ordered...
				objectArray.append([]) # Add a new element row to the 2D array...
				objectArray[j].append(allObjects[i]) # Add in this object.
				objectArray[j].append(allObjects[i].location[2]) # Get the Y position.
				j += 1

		return objectArray

	def getKeyElevations(self, ArrayOfKeys):
		keyHeight = [0, 0, 0]
		# White Key
		keyHeight[0] = ArrayOfKeys[0][1] # This is relying on the list being properly ordered, and for the first key to be white, second to be black. If this is not the case, the code will break. Sorry, I'm too tired to think of something better right now.
		# Black Key
		keyHeight[1] = ArrayOfKeys[1][1]
		# Point between black and white
		keyHeight[2] = (keyHeight[0] + keyHeight[1]) / 2 # The point between the two locations.

		return keyHeight[2]

	def sortBlackAndWhite(self, ArrayOfKeys, keyHeight):
		arrlen = len(ArrayOfKeys)
		whiteKeyList = []
		blackKeyList = []

		for i in range(arrlen):
			height = ArrayOfKeys[i][1]

			isBelowMidpoint = height < keyHeight
			if(isBelowMidpoint):
				whiteKeyList.append(ArrayOfKeys[i][0])
			else:
				blackKeyList.append(ArrayOfKeys[i][0])

		return whiteKeyList, blackKeyList



DupeKeyMaterials()
